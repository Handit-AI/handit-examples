from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from graph.state import GraphState
from graph.chains.generation import csv_generation_planner
from services.handit_service import tracker


def _nv(field: Optional[Dict[str, Any]]) -> Any:
    """Return normalized_value if present else value from a field dict."""
    if not isinstance(field, dict):
        return None
    return field.get("normalized_value") if field.get("normalized_value") is not None else field.get("value")


def _currency(field: Optional[Dict[str, Any]]) -> Optional[str]:
    if not isinstance(field, dict):
        return None
    return field.get("currency")


def _safe_join(items: Optional[List[str]]) -> Optional[str]:
    if not items:
        return None
    return " | ".join(items)


def _flatten_paths(obj: Any, prefix: str = "", limit: int = 300) -> List[Dict[str, Any]]:
    """Flatten JSON into dot-path entries with sample value and inferred type.

    Limits total entries to avoid huge prompts.
    """
    results: List[Dict[str, Any]] = []

    def visit(node: Any, path: str) -> None:
        if len(results) >= limit:
            return
        if isinstance(node, dict):
            for k, v in node.items():
                visit(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            entry = {"path": path, "type": "array", "example": None}
            results.append(entry)
            if node:
                # Visit first element as example
                visit(node[0], f"{path}[]")
        else:
            # Primitive
            t = type(node).__name__
            results.append({"path": path, "type": t, "example": node})

    visit(obj, prefix)
    return results


def _collect_documents_inventory(structured_json_paths: List[str]) -> List[Dict[str, Any]]:
    inventory: List[Dict[str, Any]] = []
    for json_path in structured_json_paths:
        try:
            p = Path(json_path)
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            paths = _flatten_paths(data)
            inventory.append({
                "path": str(p),
                "filename": p.name,
                "num_paths": len(paths),
                "paths": paths,
            })
        except Exception as e:
            inventory.append({"path": json_path, "error": str(e)})
    return inventory


def _get_value_by_path(obj: Dict[str, Any], path: str, prefer_normalized: bool) -> Any:
    # Dot path navigation; handle current array item paths starting with '.' by ignoring leading dot here
    # Normalize tokens by stripping [] from array indicators
    normalized = path.lstrip('.')
    parts = [p.replace('[]', '') for p in normalized.split('.') if p]
    current: Any = obj
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    # If the resolved value is a field object, extract a scalar; never return the dict itself
    if isinstance(current, dict):
        if prefer_normalized:
            nv = current.get("normalized_value")
            if nv is not None:
                return nv if isinstance(nv, (str, int, float, bool)) or nv is None else None
            v = current.get("value")
            if v is not None:
                return v if isinstance(v, (str, int, float, bool)) or v is None else None
            return None
        else:
            v = current.get("value")
            if v is not None:
                return v if isinstance(v, (str, int, float, bool)) or v is None else None
            nv = current.get("normalized_value")
            if nv is not None:
                return nv if isinstance(nv, (str, int, float, bool)) or nv is None else None
            return None
    # Finally, only allow scalar primitives in cells; drop lists/objects
    return current if isinstance(current, (str, int, float, bool)) or current is None else None


def _get_by_path(obj: Dict[str, Any], path: str) -> Any:
    # Normalize: remove [] array markers from path tokens
    parts = [p.replace('[]', '') for p in path.split('.') if p]
    current: Any = obj
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def generate_csv(state: GraphState) -> Dict[str, Any]:
    """Generate CSVs using an LLM plan that decides how many tables and columns are needed.

    Input: state["structured_json_paths"]: List[str]
    Output files: assets/csv/{session_id}/*.csv
    Returns updated state with CSV paths.
    """

    session_id = state.get("session_id")
    structured_json_paths: List[str] = state.get("structured_json_paths", [])
    execution_id = state.get("execution_id")

    if not session_id:
        print("❌ Missing session_id in state")
        return {**state, "errors": state.get("errors", []) + ["Missing session_id in state"]}

    if not structured_json_paths:
        print("⚠️ No structured_json_paths provided; nothing to export")
        return {**state, "errors": state.get("errors", []) + ["No structured_json_paths provided"]}

    output_dir = Path(f"assets/csv/{session_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 CSV output directory: {output_dir}")

    errors: List[str] = []

    # Build an inventory summary and call the planner chain
    inventory = _collect_documents_inventory(structured_json_paths)
    plan = csv_generation_planner.invoke({"documents_inventory": json.dumps(inventory, ensure_ascii=False)})

    # Ensure plan is a Pydantic model or dict
    plan_dict = plan.model_dump() if hasattr(plan, "model_dump") else plan
    tables = plan_dict.get("tables", [])

    generated_paths: List[str] = []

    # Load all documents into memory once
    documents: List[Dict[str, Any]] = []
    for json_path in structured_json_paths:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                documents.append({"__path__": json_path, "__name__": Path(json_path).name, "data": json.load(f)})
        except Exception as e:
            errors.append(f"Error loading {json_path}: {e}")

    for table in tables:
        name: str = table.get("name", "table")
        # Ensure the mandatory 'general' table exists: if planner omitted it, we will later synthesize it
        row_scope: str = table.get("row_scope", "per_document")
        array_path: Optional[str] = table.get("array_path")
        columns: List[Dict[str, Any]] = table.get("columns", [])

        rows: List[Dict[str, Any]] = []

        # Precompute normalized array path once
        normalized_array_path = (array_path or '').replace('[]', '') if array_path else None

        for doc in documents:
            data = doc.get("data", {})
            base_row = {"source_file": doc.get("__name__")}

            if row_scope == "per_array" and array_path:
                array_obj = _get_by_path(data, array_path)
                if isinstance(array_obj, list):
                    for item in array_obj:
                        row: Dict[str, Any] = dict(base_row)
                        for col in columns:
                            col_name = col.get("name")
                            value_path = col.get("value_path", "")
                            prefer_norm = bool(col.get("prefer_normalized", True))
                            # Resolve from current item context. Support both relative (starts with '.') and absolute paths.
                            val = None
                            if value_path.startswith('.'):
                                val = _get_value_by_path(item, value_path, prefer_norm)
                            else:
                                # Try relative by stripping the array path prefix if present
                                rel_path = value_path
                                if normalized_array_path and value_path.replace('[]', '').startswith(normalized_array_path + '.'):
                                    rel_path = value_path.replace('[]', '')[len(normalized_array_path) + 1 :]
                                    val = _get_value_by_path(item, rel_path, prefer_norm)
                                # Fallback to absolute from document root
                                if val is None:
                                    val = _get_value_by_path(data, value_path, prefer_norm)
                            row[col_name] = val
                        rows.append(row)
                else:
                    # If the array does not exist, still add a placeholder row? skip.
                    continue
            else:
                row: Dict[str, Any] = dict(base_row)
                for col in columns:
                    col_name = col.get("name")
                    value_path = col.get("value_path", "")
                    prefer_norm = bool(col.get("prefer_normalized", True))
                    row[col_name] = _get_value_by_path(data, value_path, prefer_norm)
                rows.append(row)

        # Materialize DataFrame and save CSV
        df = pd.DataFrame(rows)
        csv_path = output_dir / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved: {csv_path}")
        generated_paths.append(str(csv_path))

    # Track the LLM call
    tracker.track_node(
                 input="hola",
                 output=generated_paths,
                 node_name="generate_csv",
                 agent_name="unstructured_to_structured",
                 node_type="llm",
                 execution_id=execution_id
            )

    # If planner did not include a 'general' table, synthesize a basic one with common top-level fields
    if not any(Path(p).stem == "general" for p in generated_paths):
        rows: List[Dict[str, Any]] = []
        for doc in documents:
            data = doc.get("data", {})
            row: Dict[str, Any] = {"source_file": doc.get("__name__")}
            # Flatten a subset of top-level fields into general
            for k, v in data.items():
                if isinstance(v, dict):
                    # Prefer normalized/value if present
                    nv = v.get("normalized_value") if v.get("normalized_value") is not None else v.get("value")
                    if isinstance(nv, (str, int, float, bool)) or nv is None:
                        row[k] = nv
                    else:
                        # Do not write nested lists/objects into cells
                        row[k] = None
                elif isinstance(v, (str, int, float, bool)) or v is None:
                    row[k] = v
                else:
                    # arrays/objects summarized
                    row[k] = None
            rows.append(row)
        df = pd.DataFrame(rows)
        csv_path = output_dir / "general.csv"
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved (auto): {csv_path}")
        generated_paths.append(str(csv_path))

    updated_errors = state.get("errors", []) + errors

  

    return {**state, "csv_path": None, "details_csv_path": None, "line_items_csv_path": None, "generated_csv_paths": generated_paths, "errors": updated_errors}



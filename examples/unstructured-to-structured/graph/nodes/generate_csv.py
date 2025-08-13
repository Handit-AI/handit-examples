from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import logging
from graph.chains.generation import logged_generation_chain
from graph.state import GraphState


def _load_records(json_paths: List[str]) -> tuple[List[Dict[str, Any]], List[str]]:
    records: List[Dict[str, Any]] = []
    errors: List[str] = []
    for p in json_paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                records.append(json.load(f))
        except Exception as exc:
            errors.append(f"{p}: {exc}")
    return records, errors


def generate_csv(state: GraphState) -> Dict[str, Any]:
    """Load JSON records from state.json_paths and call generation_chain.

    Returns updated state keys: csv_content (string with CSV). Persist is done by save_csv node.
    """

    json_paths = state.get("json_paths") or []
    session_id = state.get("session_id") or "default"

    logger = logging.getLogger("graph.node.generate_csv")
    logger.info("📊 generate_csv: session_id=%s, json_paths=%d", session_id, len(json_paths))
    records, load_errors = _load_records(json_paths)
    logger.info("📥 generate_csv: loaded_records=%d, load_errors=%d", len(records), len(load_errors))

    # Prepare inputs for the chain
    filenames = [r.get("filename") or Path(p).name for r, p in zip(records, json_paths)]
    records_text = json.dumps(records, ensure_ascii=False, indent=2)

    logger.debug("generate_csv: filenames=%s", filenames)
    logger.debug("generate_csv: sample_records_text=%s", records_text[:500])
    csv_content: str = logged_generation_chain({
        "filenames": ", ".join(filenames),
        "records_text": records_text,
    })
    logger.info("📄 generate_csv: csv_len=%d", len(csv_content or ""))
    logger.info("🤖 LLM Response: %s", repr(csv_content))

    # Merge errors
    merged_errors = list(state.get("errors") or []) + load_errors

    result_state = {
        **state,
        "csv_content": csv_content,
        "errors": merged_errors,
    }
    logger.info("🔄 generate_csv returning: csv_content_len=%d, state_keys=%s", 
                len(result_state.get("csv_content", "")), list(result_state.keys()))
    return result_state



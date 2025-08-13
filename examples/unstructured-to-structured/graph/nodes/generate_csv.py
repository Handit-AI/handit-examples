from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from graph.state import GraphState


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


def generate_csv(state: GraphState) -> Dict[str, Any]:
    """Generate two CSVs: invoice-level details and flattened line items.

    Input: state["structured_json_paths"]: List[str]
    Output files: assets/csv/{session_id}/invoices.csv, assets/csv/{session_id}/line_items.csv
    Returns updated state with CSV paths.
    """

    session_id = state.get("session_id")
    structured_json_paths: List[str] = state.get("structured_json_paths", [])

    if not session_id:
        print("❌ Missing session_id in state")
        return {**state, "errors": state.get("errors", []) + ["Missing session_id in state"]}

    if not structured_json_paths:
        print("⚠️ No structured_json_paths provided; nothing to export")
        return {**state, "errors": state.get("errors", []) + ["No structured_json_paths provided"]}

    output_dir = Path(f"assets/csv/{session_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 CSV output directory: {output_dir}")

    details_rows: List[Dict[str, Any]] = []
    line_rows: List[Dict[str, Any]] = []
    errors: List[str] = []

    for json_path in structured_json_paths:
        try:
            path_obj = Path(json_path)
            with open(path_obj, "r", encoding="utf-8") as f:
                data = json.load(f)

            filename = path_obj.name

            # Invoice-level details
            details_rows.append(
                {
                    "filename": filename,
                    "document_type": data.get("document_type"),
                    "document_language": _nv(data.get("document_language")),
                    "invoice_id": _nv(data.get("invoice_id")),
                    "purchase_order": _nv(data.get("purchase_order")),
                    # Dates/terms
                    "issue_date": _nv(data.get("issue_date")) or _nv(data.get("invoice_date")),
                    "due_date": _nv(data.get("due_date")),
                    "payment_terms": _nv(data.get("payment_terms")),
                    # Seller
                    "seller_name": _nv((data.get("seller") or {}).get("name")),
                    "seller_tax_id": _nv((data.get("seller") or {}).get("tax_id")),
                    "seller_address": _nv((data.get("seller") or {}).get("address")),
                    "seller_email": _nv((data.get("seller") or {}).get("email")) or _nv((data.get("seller") or {}).get("contact")),
                    "seller_phone": _nv((data.get("seller") or {}).get("phone")),
                    # Buyer
                    "buyer_name": _nv((data.get("buyer") or {}).get("name")),
                    "buyer_tax_id": _nv((data.get("buyer") or {}).get("tax_id")),
                    "buyer_address": _nv((data.get("buyer") or {}).get("address")),
                    "buyer_email": _nv((data.get("buyer") or {}).get("email")) or _nv((data.get("buyer") or {}).get("contact")),
                    "buyer_phone": _nv((data.get("buyer") or {}).get("phone")),
                    # Currency/amounts
                    "currency": _nv(data.get("currency")) or _currency(data.get("grand_total")) or _currency(data.get("subtotal")),
                    "subtotal": _nv(data.get("subtotal")),
                    "subtotal_currency": _currency(data.get("subtotal")),
                    "total_tax": _nv(data.get("total_tax")) or _nv(data.get("tax_amount")),
                    "total_tax_currency": _currency(data.get("total_tax")) or _currency(data.get("tax_amount")),
                    "total_discount": _nv(data.get("total_discount")) or _nv(data.get("discount_amount")),
                    "total_discount_currency": _currency(data.get("total_discount")) or _currency(data.get("discount_amount")),
                    "shipping": _nv(data.get("shipping")) or _nv(data.get("shipping_amount")),
                    "shipping_currency": _currency(data.get("shipping")) or _currency(data.get("shipping_amount")),
                    "grand_total": _nv(data.get("grand_total")),
                    "grand_total_currency": _currency(data.get("grand_total")),
                    # Notes / warnings / checks
                    "notes": _nv(data.get("notes")),
                    "parsing_warnings": _safe_join(data.get("parsing_warnings")),
                    "checks": _safe_join(data.get("checks")),
                }
            )

            # Line items
            line_items = data.get("line_items") or []
            for idx, item in enumerate(line_items, start=1):
                line_rows.append(
                    {
                        "filename": filename,
                        "line_index": idx,
                        "description": _nv(item.get("description")),
                        "sku": _nv(item.get("sku")),
                        "quantity": _nv(item.get("quantity")),
                        "unit_price": _nv(item.get("unit_price")),
                        "unit_price_currency": _currency(item.get("unit_price")),
                        "discount": _nv(item.get("discount")),
                        "discount_currency": _currency(item.get("discount")),
                        "tax": _nv(item.get("tax")),
                        "tax_currency": _currency(item.get("tax")),
                        "line_total": _nv(item.get("line_total")),
                        "line_total_currency": _currency(item.get("line_total")),
                    }
                )

        except Exception as e:
            err = f"Error processing {json_path}: {e}"
            print(f"❌ {err}")
            errors.append(err)
            continue

    # Build DataFrames and write CSVs
    details_df = pd.DataFrame(details_rows)
    line_df = pd.DataFrame(line_rows)

    details_csv_path = output_dir / "invoices.csv"
    line_items_csv_path = output_dir / "line_items.csv"

    details_df.to_csv(details_csv_path, index=False)
    line_df.to_csv(line_items_csv_path, index=False)

    print(f"✅ Saved: {details_csv_path}")
    print(f"✅ Saved: {line_items_csv_path}")

    updated_errors = state.get("errors", []) + errors

    return {
        **state,
        "details_csv_path": str(details_csv_path),
        "line_items_csv_path": str(line_items_csv_path),
        "errors": updated_errors,
    }



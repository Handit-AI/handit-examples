from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, TypedDict


class GraphState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes for ingestion.

    Keys:
    - session_id: Unique identifier for a processing session
    - json_paths: List of JSON file paths produced by processing
    - unstructured_paths: List of paths to uploaded unstructured files
    - classification_results: Dictionary containing document classification results
    - invoices_paths: List of paths to files classified as invoices
    - structured_json_paths: List of paths to structured JSON files from invoice data extraction
    - csv_content: Generated CSV content as string
    - csv_path: Path where CSV was saved
    - errors: Any non-fatal errors encountered during processing
    """

    session_id: str
    json_paths: List[str]
    unstructured_paths: List[str]
    structured_json_paths: List[str]
    details_csv_path: str
    line_items_csv_path: str
    classification_results: Dict[str, Any]
    invoices_paths: List[str]
    csv_content: str
    csv_path: str
    errors: List[str]
    execution_id: str



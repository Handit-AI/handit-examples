from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, TypedDict


class GraphState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes for ingestion.

    Keys:
    - session_id: Unique identifier for a processing session
    - json_paths: List of JSON file paths produced by processing
    - csv_content: Generated CSV content as string
    - csv_path: Path where CSV was saved
    - errors: Any non-fatal errors encountered during processing
    """

    session_id: str
    json_paths: List[str]
    csv_content: str
    csv_path: str
    errors: List[str]



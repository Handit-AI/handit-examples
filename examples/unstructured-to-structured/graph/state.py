from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, TypedDict


class GraphState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes for ingestion.

    Keys:
    - session_id: Unique identifier for a processing session
    - files: List of (content bytes, filename, content_type) to process
    - results: Per-file results with saved JSON paths and metadata
    - errors: Any non-fatal errors encountered during processing
    """

    session_id: str
    files: List[Tuple[bytes, str, Optional[str]]]
    results: List[Dict[str, Any]]
    errors: List[str]



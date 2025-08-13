from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import logging
from graph.state import GraphState


def save_csv(state: GraphState) -> Dict[str, Any]:
    """Persist csv_content in assets/outputs/{session_id}/combined.csv and return csv_path.
    """

    logger = logging.getLogger("graph.node.save_csv")
    
    session_id = state.get("session_id") or "default"
    csv_content = state.get("csv_content") or ""
    
    # Fallback: if csv_content is empty, try to get it from the previous node's output
    if not csv_content and "csv_content" not in state:
        logger.warning("⚠️ csv_content not found in state, this suggests a state propagation issue")
        # Create a minimal CSV as fallback
        csv_content = "filename,session_id,error\nempty,state_propagation_failed,missing_csv_content"
    logger.info("💾 save_csv: session_id=%s, content_len=%d", session_id, len(csv_content or ""))
    logger.info("🔍 save_csv received state keys: %s", list(state.keys()))
    logger.info("🔍 save_csv csv_content type: %s, value: %s", type(csv_content), repr(csv_content[:100]))

    output_dir = Path("assets/outputs") / session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "combined.csv"
    with csv_path.open("w", encoding="utf-8") as f:
        f.write(csv_content)
    logger.info("✅ save_csv: wrote %s", csv_path)

    return {
        **state,
        "csv_path": str(csv_path),
    }



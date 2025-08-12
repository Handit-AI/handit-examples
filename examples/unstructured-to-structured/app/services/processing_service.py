from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from app.domain.ports.llm_client import LLMClient
from app.config.settings import settings


class ProcessingService:
    def __init__(self, llm_client: LLMClient):
        self._llm = llm_client

    async def process_bulk(
        self,
        *,
        session_id: str,
        files: Iterable[Tuple[bytes, str, str | None]],
    ) -> List[Dict[str, Any]]:
        """Process a bulk of files and persist structured JSON per file.

        files: iterable of tuples (content, filename, content_type)
        """
        output_dir = Path(settings.outputs_dir) / session_id
        output_dir.mkdir(parents=True, exist_ok=True)

        results: List[Dict[str, Any]] = []
        for content, filename, content_type in files:
            structured = await self._llm.extract_structured(
                content=content, filename=filename, content_type=content_type
            )
            record = {
                "session_id": session_id,
                "filename": filename,
                "content_type": content_type,
                "data": structured,
            }
            out_path = output_dir / f"{Path(filename).stem}.json"
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            results.append({"filename": filename, "json_path": str(out_path)})

        return results



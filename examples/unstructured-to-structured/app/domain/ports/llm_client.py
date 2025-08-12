from typing import Protocol, Dict, Any


class LLMClient(Protocol):
    async def extract_structured(self, *, content: bytes, filename: str, content_type: str | None) -> Dict[str, Any]:
        """Return structured JSON describing the document contents (OCR-like)."""



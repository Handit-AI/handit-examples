from __future__ import annotations

import base64
import json
import mimetypes
from typing import Any, Dict

from app.domain.ports.llm_client import LLMClient
from app.config.settings import settings


class OpenAILLMClient(LLMClient):
    def __init__(self, api_key: str, model: str | None = None):
        from openai import OpenAI  # import lazily to keep optional dependency

        self._client = OpenAI(api_key=api_key)
        self._model = model or settings.openai_model

    def _build_messages(self, *, content: bytes, filename: str, content_type: str | None) -> list[dict]:
        system_prompt = """You are a meticulous information-extraction engine. Work ONLY with the text you are given (OCR or plain). You must return a single JSON object that strictly follows the schema below. Do not include any extra text.

Rules for high accuracy:
- Do NOT invent values. If a value is not explicitly present, return null and explain in "reason".
- For each field, copy the exact substring from the document into "raw". Provide a normalized value in "normalized" (ISO 8601 for dates; dot-decimal numbers; ISO 4217 for currency; trimmed whitespace; language-agnostic numerics).
- Always include evidence: either page/line/char spans when known OR a short "snippet". If available, include a bounding box "bbox": [x1,y1,x2, y2] in page coordinates (pixels or normalized 0–1).
- For tables, preserve row order and copy raw cell substrings; also provide numeric normalization where applicable in "normalized_rows".
- If totals don't match the sum of items, DO NOT fix them. Report the discrepancy in "checks".
- Multilingual: documents may be in any language. Keep "raw" as-is; normalize numerics/dates/currency in a language-agnostic way.
- If "target_fields" is empty, auto-discover key–value fields present in the document. Also set "document_type" (e.g., "invoice", "receipt", "id_card", "bank_statement", or "unknown").
- Output JSON only. No prose, no explanations outside the JSON.

Output schema (strict JSON):
{
  "document_id": string,
  "document_type": string | null,
  "language": string | null,
  "fields": [
    {
      "name": string,
      "raw": string | null,
      "normalized": string | number | boolean | null,
      "confidence": number,
      "reason": string | null,
      "evidence": [
        {
          "page": number | null,
          "line": number | null,
          "char_start": number | null,
          "char_end": number | null,
          "snippet": string | null,
          "bbox": [number, number, number, number] | null
        }
      ]
    }
  ],
  "tables": [
    {
      "name": string,
      "columns": [string],
      "rows": [[string]],
      "normalized_rows": [[string | number | boolean | null]],
      "confidence": number,
      "evidence": [
        { "page": number | null, "snippet": string | null }
      ]
    }
  ],
  "checks": [
    { "type": "math_mismatch" | "format_warning" | "missing_field", "detail": string }
  ]
}"""

        user_prompt = """Extract the requested information from the following document content using the System Prompt rules and schema.
"""

        inferred = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        if inferred.startswith("text/"):
            try:
                text = content.decode("utf-8", errors="replace")
            except Exception:
                text = ""
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_prompt}\n\nDocument name: {filename}\n\nContent:\n{text}"},
            ]
        else:
            b64 = base64.b64encode(content).decode("utf-8") if content else ""
            data_url = f"data:{inferred};base64,{b64}"
            return [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ]

    async def extract_structured(self, *, content: bytes, filename: str, content_type: str | None) -> Dict[str, Any]:
        msgs = self._build_messages(content=content, filename=filename, content_type=content_type)
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=msgs,
            temperature=0.0,
        )
        text = resp.choices[0].message.content or "{}"
        try:
            return json.loads(text)
        except Exception:
            try:
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1:
                    return json.loads(text[start : end + 1])
            except Exception:
                pass
            return {"raw": text}



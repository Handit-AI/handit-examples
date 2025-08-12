from typing import List
import logging

from fastapi import APIRouter, File, Form, UploadFile

from app.config.settings import settings
from app.services.processing_service import ProcessingService
from app.adapters.llm.openai_client import OpenAILLMClient


logger = logging.getLogger("app.documents")

router = APIRouter(prefix="/documents", tags=["documents"])


def get_processing_service() -> ProcessingService:
    # Auto-select LLM client from settings
    if not settings.openai_api_key:
        # Fail early if no key configured
        raise RuntimeError("OPENAI_API_KEY not configured. Set it in .env")
    logger.info("🤖 Using OpenAI model '%s'", settings.openai_model)
    llm = OpenAILLMClient(api_key=settings.openai_api_key, model=settings.openai_model)
    return ProcessingService(llm_client=llm)


@router.post("/bulk-process")
async def bulk_process(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...),
):
    logger.info("📥 Bulk process request: session=%s, files=%d", session_id, len(files))
    logger.debug("🗂️ Files: %s", [f.filename for f in files])

    svc = get_processing_service()
    try:
        contents = [await f.read() for f in files]
        triplets = [
            (content, f.filename, f.content_type) for content, f in zip(contents, files)
        ]
        results = await svc.process_bulk(session_id=session_id, files=triplets)
        logger.info("✅ Processed %d file(s) for session %s", len(results), session_id)
        for r in results:
            logger.debug("💾 Saved %s -> %s", r["filename"], r["json_path"])
        return {"session_id": session_id, "saved": results}
    except Exception as exc:
        logger.exception("💥 Error processing bulk for session %s: %s", session_id, exc)
        raise



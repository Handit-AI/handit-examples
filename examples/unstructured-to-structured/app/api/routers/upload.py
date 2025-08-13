from typing import List
import logging

from fastapi import APIRouter, File, Form, UploadFile

from app.config.settings import settings
from app.services.processing_service import ProcessingService
from app.adapters.llm.openai_client import OpenAILLMClient
from graph.graph import run_test_graph, run_csv_graph


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
        # Collect JSON paths for the test graph
        json_paths = [r["json_path"] for r in results]
        # Run simple test graph to propagate state
        graph_state = run_test_graph(json_paths)
        # Run CSV generation graph
        csv_state = run_csv_graph(session_id=session_id, json_paths=json_paths)
        logger.info("✅ Processed %d file(s) for session %s", len(results), session_id)
        for r in results:
            logger.debug("💾 Saved %s -> %s", r["filename"], r["json_path"])
        return {
            "session_id": session_id,
            "saved": results,
            "message": f"Done, las rutas de los archivos son: {', '.join(graph_state.get('json_paths', []))}",
            "csv_path": csv_state.get("csv_path"),
        }
    except Exception as exc:
        logger.exception("💥 Error processing bulk for session %s: %s", session_id, exc)
        raise



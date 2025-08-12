from fastapi import APIRouter
from time import time

from app.config.settings import settings


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", include_in_schema=False)
async def read_health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
        "ts": time(),
    }



from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.upload import router as upload_router
from app.config.settings import settings


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, version=settings.version)
    application.include_router(health_router)
    application.include_router(upload_router)
    return application


app = create_app()



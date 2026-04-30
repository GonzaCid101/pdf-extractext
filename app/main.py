"""Entry point de la aplicación FastAPI."""

from fastapi import FastAPI

from app.api.endpoints.pdfs import router as pdfs_router
from app.api.endpoints.upload import router as upload_router
from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(title=settings.APP_TITLE)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(pdfs_router)

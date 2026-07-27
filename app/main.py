"""Entry point de la aplicación FastAPI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.endpoints.pdfs import router as pdfs_router
from app.api.endpoints.upload import router as upload_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.middleware import TracingMiddleware
from app.exceptions.rfc9457 import RFC9457Exception

from app.repository.database import get_database
from app.repository.pdf_repository import PDFRepository

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async for db in get_database():
        repo = PDFRepository(db)
        await repo.setup_indexes()
        break
    
    yield
    
    pass

app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)

app.add_middleware(TracingMiddleware)

@app.exception_handler(RFC9457Exception)
async def rfc9457_exception_handler(request: Request, exc: RFC9457Exception):
    return JSONResponse(
        status_code=exc.status,
        content=exc.to_dict(),
        media_type="application/problem+json",
    )

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(pdfs_router)
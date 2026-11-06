"""Entry point de la aplicación FastAPI."""

from contextlib import asynccontextmanager
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.endpoints.pdfs import router as pdfs_router
from app.api.endpoints.upload import router as upload_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.middleware import TracingMiddleware
from app.domain.exceptions import DuplicatePDFError, PDFNotFoundError
from app.exceptions.rfc9457 import (
    DuplicatePDFException,
    PDFNotFoundException,
    RFC9457Exception,
)
from app.repository.database import mongo_manager
from app.repository.pdf_repository import PDFRepository

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        await PDFRepository(mongo_manager.get_client()).setup_indexes()
        yield
    finally:
        await mongo_manager.close()


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)

app.add_middleware(TracingMiddleware)


def _problem_response(problem: RFC9457Exception) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        content=problem.to_dict(),
        media_type="application/problem+json",
    )


@app.exception_handler(RFC9457Exception)
async def rfc9457_exception_handler(request: Request, exc: RFC9457Exception):
    return _problem_response(exc)


# Traducción única en la capa API: excepción pura de dominio -> RFC 9457.
@app.exception_handler(DuplicatePDFError)
async def duplicate_pdf_error_handler(request: Request, exc: DuplicatePDFError):
    problem = DuplicatePDFException(
        detail=str(exc) or "El documento ya existe en el sistema",
        instance=str(request.url.path),
    )
    return _problem_response(problem)


# FASE GREEN: Traducción centralizada del 404 de dominio a RFC 9457.
@app.exception_handler(PDFNotFoundError)
async def pdf_not_found_error_handler(request: Request, exc: PDFNotFoundError):
    problem = PDFNotFoundException(
        detail=str(exc) or "PDF no encontrado",
        instance=str(request.url.path),
    )
    return _problem_response(problem)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Error interno no controlado")
    problem = RFC9457Exception(
        type_="about:blank",
        title="Error interno del servidor",
        status=500,
        detail="Error interno del servidor",
        instance=str(request.url.path),
    )
    return _problem_response(problem)


app.include_router(health_router)
app.include_router(upload_router)
app.include_router(pdfs_router)


def run() -> None:
    uvicorn.run(
        "app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, workers=4
    )


if __name__ == "__main__":
    run()

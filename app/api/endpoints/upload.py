"""Endpoint para subida de archivos PDF."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.pdf_models import PDFDocumentResponse
from app.repository.database import get_database
from app.services.pdf_service import DuplicatePDFError, process_and_save_pdf

router = APIRouter()


@router.post(
    "/upload-pdf",
    response_model=PDFDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_pdf(
    file: UploadFile = File(...),
    db: AsyncIOMotorClient = Depends(get_database),
) -> PDFDocumentResponse:
    """Procesa PDF, guarda en BD y retorna datos con ID."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Solo se permiten archivos PDF")

    pdf_bytes = await file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    try:
        result = await process_and_save_pdf(db, file.filename, pdf_bytes)
    except DuplicatePDFError:
        raise HTTPException(
            status_code=409, detail="El documento ya existe en el sistema"
        )

    return PDFDocumentResponse(**result)

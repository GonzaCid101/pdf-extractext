"""Endpoint para carga y validación de archivos PDF."""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.pdf_models import PDFDocumentResponse
from app.services.pdf_service import extract_text_from_pdf
from app.services.checksum import generate_checksum

router = APIRouter()


@router.post("/upload-pdf", response_model=PDFDocumentResponse)
async def upload_pdf(file: UploadFile = File(...)) -> PDFDocumentResponse:
    """Carga un PDF, valida la extensión y extrae su texto."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Solo se permiten archivos PDF")

    pdf_bytes = await file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    extracted_text = extract_text_from_pdf(pdf_bytes)
    checksum = generate_checksum(pdf_bytes)

    return PDFDocumentResponse(
        filename=file.filename, extracted_text=extracted_text, checksum=checksum
    )

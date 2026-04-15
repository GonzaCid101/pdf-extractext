"""Endpoint para carga y validación de archivos PDF."""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_service import extract_text_from_pdf

router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    """Carga un PDF, valida la extensión y extrae su texto."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Solo se permiten archivos PDF")

    pdf_bytes = await file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    extracted_text = extract_text_from_pdf(pdf_bytes)

    return {"filename": file.filename, "extracted_text": extracted_text}

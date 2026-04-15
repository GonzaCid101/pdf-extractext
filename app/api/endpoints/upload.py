"""
Endpoint para carga y validación de archivos PDF.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_service import extract_text_from_pdf

router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    """
    Carga un archivo PDF y extrae su texto.

    Args:
        file: Archivo PDF a cargar.

    Returns:
        JSON con el nombre del archivo y el texto extraído.

    Raises:
        HTTPException: 415 si el archivo no es PDF.
        HTTPException: 400 si el archivo está vacío.
    """
    # Validate PDF extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=415, detail="Unsupported Media Type: Only PDF files are allowed"
        )

    # Read PDF bytes
    pdf_bytes = await file.read()

    # Validate file is not empty
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Bad Request: File is empty")

    # Extract text from PDF bytes
    extracted_text = extract_text_from_pdf(pdf_bytes)

    return {"filename": file.filename, "extracted_text": extracted_text}

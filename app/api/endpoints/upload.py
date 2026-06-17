"""Endpoint para subida de archivos PDF."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.api.dependencies import get_pdf_service
from app.core.config import settings
from app.exceptions.rfc9457 import DuplicatePDFException
from app.models.pdf_models import PDFDocumentResponse
from app.services.pdf_service import PDFService, DuplicatePDFError
router = APIRouter()
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends

router = APIRouter()

@router.post(
    "/upload-pdf",
    response_model=PDFDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_pdf(
    file: UploadFile = File(...),
    service: PDFService = Depends(get_pdf_service),
) -> PDFDocumentResponse:
    
    if not file.filename or not file.filename.lower().endswith(
        settings.ALLOWED_FILE_EXTENSION
    ):
        raise HTTPException(status_code=415, detail="Solo se permiten archivos PDF")
        
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="El formato debe ser application/pdf")

    pdf_bytes = await file.read()
    
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
        
    
    if len(pdf_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="El archivo excede el tamaño máximo permitido (50MB)")

    
    try:
        result = await service.process_and_save(file.filename, pdf_bytes)
    except DuplicatePDFError:
        raise DuplicatePDFException()
    except ValueError as e:
        
        raise HTTPException(status_code=400, detail=str(e))

    return PDFDocumentResponse(**result)
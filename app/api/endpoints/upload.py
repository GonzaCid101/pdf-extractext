from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.api.dependencies import get_pdf_service
from app.core.config import settings
from app.exceptions.rfc9457 import DuplicatePDFException
from app.models.pdf_models import PDFDocumentResponse
from app.services.pdf_service import PDFService, DuplicatePDFError

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
    
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    
    if file.size is not None and file.size > max_size_bytes:
        raise HTTPException(
            status_code=413, 
            detail=f"El archivo supera el límite máximo de {settings.MAX_FILE_SIZE_MB} MB"
        )

    real_size = 0
    pdf_bytes_array = bytearray()
    
    while chunk := await file.read(1024 * 1024):
        real_size += len(chunk)
        if real_size > max_size_bytes:
            raise HTTPException(
                status_code=413, 
                detail=f"El archivo supera el límite máximo de {settings.MAX_FILE_SIZE_MB} MB"
            )
        pdf_bytes_array.extend(chunk)
        
    pdf_bytes = bytes(pdf_bytes_array)

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
        
    try:
        result = await service.process_and_save(file.filename, pdf_bytes)
    except DuplicatePDFError:
        raise DuplicatePDFException()
        
    return PDFDocumentResponse(**result)
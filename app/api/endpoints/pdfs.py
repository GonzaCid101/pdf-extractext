"""Endpoints para consultar documentos PDF guardados."""

import re

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_pdf_service
from app.domain.pdf_document import PDFDocument
from app.exceptions.rfc9457 import InvalidObjectIdException
from app.models.pdf_models import PDFDocumentResponse, PDFUpdateRequest
from app.services.pdf_service import PDFNotFoundError, PDFService

router = APIRouter()

_OBJECT_ID_PATTERN = re.compile(r"^[0-9a-fA-F]{24}$")


def _to_response(document: PDFDocument) -> PDFDocumentResponse:
    """Mapeo explícito de entidad de dominio a DTO de respuesta."""
    return PDFDocumentResponse(
        id=document.id,
        filename=document.filename,
        extracted_text=document.extracted_text,
        checksum=document.checksum,
    )


def _validate_object_id(pdf_id: str) -> None:
    if not _OBJECT_ID_PATTERN.fullmatch(pdf_id):
        raise InvalidObjectIdException(instance=f"/pdfs/{pdf_id}")


@router.get("/pdfs", response_model=list[PDFDocumentResponse])
async def get_all_pdfs(
    service: PDFService = Depends(get_pdf_service),
):
    documents = await service.get_all()
    return [_to_response(doc) for doc in documents]


@router.get("/pdfs/{pdf_id}", response_model=PDFDocumentResponse)
async def get_pdf_by_id(
    pdf_id: str,
    service: PDFService = Depends(get_pdf_service),
):
    _validate_object_id(pdf_id)
    try:
        document = await service.get_by_id(pdf_id)
    except PDFNotFoundError:
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return _to_response(document)


@router.patch("/pdfs/{pdf_id}", response_model=PDFDocumentResponse)
async def patch_pdf(
    pdf_id: str,
    update_data: PDFUpdateRequest,
    service: PDFService = Depends(get_pdf_service),
):
    _validate_object_id(pdf_id)
    if update_data.filename is None:
        raise HTTPException(
            status_code=400,
            detail="No se proporcionó ningún campo para actualizar",
        )
    try:
        document = await service.update_filename(pdf_id, update_data.filename)
    except PDFNotFoundError:
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return _to_response(document)


@router.delete("/pdfs/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf(
    pdf_id: str,
    service: PDFService = Depends(get_pdf_service),
):
    _validate_object_id(pdf_id)
    try:
        await service.delete(pdf_id)
    except PDFNotFoundError:
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return None

"""Endpoints para consultar documentos PDF guardados."""

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_pdf_repository
from app.domain.pdf_document import PDFDocument
from app.exceptions.rfc9457 import InvalidObjectIdException
from app.models.pdf_models import PDFUpdateRequest
from app.repository.pdf_repository import PDFRepository

router = APIRouter()


def _serialize_document(document: PDFDocument) -> dict:
    return {
        "id": document.id,
        "filename": document.filename,
        "extracted_text": document.extracted_text,
        "checksum": document.checksum,
    }


def _validate_object_id(pdf_id: str) -> None:
    if not ObjectId.is_valid(pdf_id):
        raise InvalidObjectIdException(instance=f"/pdfs/{pdf_id}")


@router.get("/pdfs")
async def get_all_pdfs(
    repository: PDFRepository = Depends(get_pdf_repository),
):
    documents = await repository.get_all()
    return [_serialize_document(doc) for doc in documents]


@router.get("/pdfs/{pdf_id}")
async def get_pdf_by_id(
    pdf_id: str,
    repository: PDFRepository = Depends(get_pdf_repository),
):
    _validate_object_id(pdf_id)
    document = await repository.find_by_id(pdf_id)
    if document is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return _serialize_document(document)


@router.patch("/pdfs/{pdf_id}")
async def patch_pdf(
    pdf_id: str,
    update_data: PDFUpdateRequest,
    repository: PDFRepository = Depends(get_pdf_repository),
):
    _validate_object_id(pdf_id)
    existing = await repository.find_by_id(pdf_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
    await repository.update(pdf_id, update_dict)

    updated = await repository.find_by_id(pdf_id)
    return _serialize_document(updated)


@router.delete("/pdfs/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf(
    pdf_id: str,
    repository: PDFRepository = Depends(get_pdf_repository),
):
    _validate_object_id(pdf_id)
    existing = await repository.find_by_id(pdf_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    await repository.delete(pdf_id)

    return None

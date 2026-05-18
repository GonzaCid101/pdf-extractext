"""Endpoints para consultar documentos PDF guardados."""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.dependencies import get_pdf_repository
from app.models.pdf_models import PDFUpdateRequest
from app.repository.database import get_database
from app.repository.pdf_repository import PDFRepository

router = APIRouter()


def _serialize_document(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/pdfs")
async def get_all_pdfs(
    db: AsyncIOMotorClient = Depends(get_database),
):
    documents = []
    async for doc in db.pdf_db.pdfs.find():
        documents.append(_serialize_document(doc))
    return documents


@router.get("/pdfs/{pdf_id}")
async def get_pdf_by_id(
    pdf_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
    repository: PDFRepository = Depends(get_pdf_repository),
):
    document = await repository.find_by_id(pdf_id)
    if document is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return _serialize_document(document)


@router.patch("/pdfs/{pdf_id}")
async def patch_pdf(
    pdf_id: str,
    update_data: PDFUpdateRequest,
    db: AsyncIOMotorClient = Depends(get_database),
    repository: PDFRepository = Depends(get_pdf_repository),
):
    existing = await repository.find_by_id(pdf_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
    await repository.update(pdf_id, update_dict)

    updated = await repository.find_by_id(pdf_id)
    return _serialize_document(updated)


@router.delete("/pdfs/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf_endpoint(
    pdf_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
    repository: PDFRepository = Depends(get_pdf_repository),
):
    existing = await repository.find_by_id(pdf_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    await repository.delete(pdf_id)

    return None

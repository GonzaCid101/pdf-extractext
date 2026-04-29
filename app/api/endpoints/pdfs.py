"""Endpoints para consultar documentos PDF guardados."""

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.pdf_models import PDFUpdateRequest
from app.repository.database import get_database
from app.repository.pdf_repository import (
    delete_pdf,
    find_by_id,
    update_pdf,
)

router = APIRouter()


def _serialize_document(doc: dict) -> dict:
    """Convierte ObjectId a string en el documento."""
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/pdfs")
async def get_all_pdfs(db: AsyncIOMotorClient = Depends(get_database)):
    """Retorna todos los documentos PDF guardados."""
    documents = []
    async for doc in db.pdf_db.pdfs.find():
        documents.append(_serialize_document(doc))
    return documents


@router.get("/pdfs/{pdf_id}")
async def get_pdf_by_id(pdf_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    """Retorna un documento PDF específico por su ID."""
    document = await find_by_id(db, pdf_id)
    if document is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return _serialize_document(document)


@router.patch("/pdfs/{pdf_id}")
async def patch_pdf(
    pdf_id: str,
    update_data: PDFUpdateRequest,
    db: AsyncIOMotorClient = Depends(get_database),
):
    """Actualiza metadatos de un documento PDF existente.

    Solo permite modificar el filename. Los campos checksum y extracted_text
    son inmutables para garantizar la integridad del documento.

    Args:
        pdf_id: ID del documento PDF.
        update_data: Datos a actualizar (solo filename).
        db: Cliente de base de datos.

    Returns:
        Documento PDF actualizado.

    Raises:
        HTTPException: 404 si el PDF no existe.
    """
    # Verificar que el documento existe
    existing = await find_by_id(db, pdf_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    # Preparar datos de actualización (solo campos no nulos)
    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)

    # Ejecutar actualización
    await update_pdf(db, pdf_id, update_dict)

    # Retornar documento actualizado
    updated = await find_by_id(db, pdf_id)
    return _serialize_document(updated)


@router.delete("/pdfs/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf_endpoint(
    pdf_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
):
    """Elimina físicamente un documento PDF de la base de datos.

    Args:
        pdf_id: ID del documento PDF a eliminar.
        db: Cliente de base de datos.

    Returns:
        None (HTTP 204 No Content).

    Raises:
        HTTPException: 404 si el PDF no existe.
    """
    # Verificar que el documento existe antes de eliminar
    existing = await find_by_id(db, pdf_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    # Ejecutar eliminación física
    await delete_pdf(db, pdf_id)

    return None

"""Endpoints para consultar documentos PDF guardados."""

from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient

from app.repository.database import get_database

router = APIRouter()


def _is_valid_objectid(pdf_id: str) -> ObjectId | None:
    """Valida y convierte string a ObjectId."""
    try:
        return ObjectId(pdf_id)
    except InvalidId:
        return None


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
    obj_id = _is_valid_objectid(pdf_id)
    if obj_id is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    document = await db.pdf_db.pdfs.find_one({"_id": obj_id})
    if document is None:
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    return _serialize_document(document)

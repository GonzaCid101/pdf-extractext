"""Operaciones CRUD para documentos PDF en MongoDB."""

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


async def save_pdf(db: AsyncIOMotorClient, document: dict) -> str:
    """Guarda un documento PDF y retorna su ID como string."""
    result = await db.pdf_db.pdfs.insert_one(document)
    return str(result.inserted_id)


async def find_by_checksum(db: AsyncIOMotorClient, checksum: str) -> dict | None:
    """Busca un documento por su checksum."""
    return await db.pdf_db.pdfs.find_one({"checksum": checksum})


async def find_by_id(db: AsyncIOMotorClient, pdf_id: str) -> dict | None:
    """Busca un documento por su ID.

    Args:
        db: Cliente de MongoDB.
        pdf_id: ID del documento como string.

    Returns:
        Documento encontrado o None si no existe.
    """
    return await db.pdf_db.pdfs.find_one({"_id": ObjectId(pdf_id)})


async def update_pdf(db: AsyncIOMotorClient, pdf_id: str, update_data: dict) -> bool:
    """Actualiza un documento PDF por su ID.

    Args:
        db: Cliente de MongoDB.
        pdf_id: ID del documento como string.
        update_data: Diccionario con campos a actualizar.

    Returns:
        True si el documento fue modificado, False en caso contrario.
    """
    result = await db.pdf_db.pdfs.update_one(
        {"_id": ObjectId(pdf_id)}, {"$set": update_data}
    )
    return result.modified_count > 0


async def delete_pdf(db: AsyncIOMotorClient, pdf_id: str) -> bool:
    """Elimina físicamente un documento PDF por su ID.

    Args:
        db: Cliente de MongoDB.
        pdf_id: ID del documento como string.

    Returns:
        True si el documento fue eliminado, False si no existía.
    """
    result = await db.pdf_db.pdfs.delete_one({"_id": ObjectId(pdf_id)})
    return result.deleted_count > 0

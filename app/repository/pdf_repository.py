"""Operaciones CRUD para documentos PDF en MongoDB."""

from motor.motor_asyncio import AsyncIOMotorClient


async def save_pdf(db: AsyncIOMotorClient, document: dict) -> str:
    """Guarda un documento PDF y retorna su ID como string."""
    result = await db.pdf_db.pdfs.insert_one(document)
    return str(result.inserted_id)


async def find_by_checksum(db: AsyncIOMotorClient, checksum: str) -> dict | None:
    """Busca un documento por su checksum."""
    return await db.pdf_db.pdfs.find_one({"checksum": checksum})

"""Operaciones CRUD para documentos PDF en MongoDB."""

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


async def save_pdf(db: AsyncIOMotorClient, document: dict) -> str:
    result = await db[settings.MONGO_DATABASE_NAME][
        settings.MONGO_COLLECTION_NAME
    ].insert_one(document)
    return str(result.inserted_id)


async def find_by_checksum(db: AsyncIOMotorClient, checksum: str) -> dict | None:
    return await db[settings.MONGO_DATABASE_NAME][
        settings.MONGO_COLLECTION_NAME
    ].find_one({"checksum": checksum})


async def find_by_id(db: AsyncIOMotorClient, pdf_id: str) -> dict | None:
    return await db[settings.MONGO_DATABASE_NAME][
        settings.MONGO_COLLECTION_NAME
    ].find_one({"_id": ObjectId(pdf_id)})


async def update_pdf(db: AsyncIOMotorClient, pdf_id: str, update_data: dict) -> bool:
    result = await db[settings.MONGO_DATABASE_NAME][
        settings.MONGO_COLLECTION_NAME
    ].update_one({"_id": ObjectId(pdf_id)}, {"$set": update_data})
    return result.modified_count > 0


async def delete_pdf(db: AsyncIOMotorClient, pdf_id: str) -> bool:
    result = await db[settings.MONGO_DATABASE_NAME][
        settings.MONGO_COLLECTION_NAME
    ].delete_one({"_id": ObjectId(pdf_id)})
    return result.deleted_count > 0

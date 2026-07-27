"""Operaciones CRUD para documentos PDF en MongoDB."""

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from app.core.config import settings


class DuplicateRecordError(Exception):
    pass


class PDFRepository:
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self._collection = db[settings.MONGO_DATABASE_NAME][
            settings.MONGO_COLLECTION_NAME
        ]

    async def setup_indexes(self) -> None:
        """
        Crea un índice único en el campo 'checksum' para evitar duplicados.
        Debe llamarse una vez durante la inicialización de la aplicación.
        """
        await self._collection.create_index("checksum", unique=True)

    async def save(self, document: dict) -> str:
        try:
            result = await self._collection.insert_one(document)
            return str(result.inserted_id)
        except DuplicateKeyError as error:
            raise DuplicateRecordError(
                "Document with same checksum already exists"
            ) from error

    async def find_by_checksum(self, checksum: str) -> dict | None:
        return await self._collection.find_one({"checksum": checksum})

    async def find_by_id(self, pdf_id: str) -> dict | None:
        return await self._collection.find_one({"_id": ObjectId(pdf_id)})

    async def update(self, pdf_id: str, update_data: dict) -> bool:
        result = await self._collection.update_one(
            {"_id": ObjectId(pdf_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete(self, pdf_id: str) -> bool:
        result = await self._collection.delete_one({"_id": ObjectId(pdf_id)})
        return result.deleted_count > 0

    async def get_all(self) -> list[dict]:
        documents = []
        async for doc in self._collection.find():
            documents.append(doc)
        return documents

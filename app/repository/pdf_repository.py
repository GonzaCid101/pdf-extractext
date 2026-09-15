"""Operaciones CRUD para documentos PDF en MongoDB."""

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.domain.pdf_document import PDFDocument
from app.repository.mappers import domain_to_mongo, mongo_to_domain


class DuplicateRecordError(Exception):
    pass


class PDFRepository:
    def __init__(self, client: AsyncIOMotorClient) -> None:
        self._collection = client[settings.MONGO_DATABASE_NAME][
            settings.MONGO_COLLECTION_NAME
        ]

    async def setup_indexes(self) -> None:
        await self._collection.create_index("checksum", unique=True)

    async def save(self, document: PDFDocument) -> str:
        try:
            result = await self._collection.insert_one(domain_to_mongo(document))
            return str(result.inserted_id)
        except DuplicateKeyError as error:
            raise DuplicateRecordError(
                "Document with same checksum already exists"
            ) from error

    async def find_by_id(self, pdf_id: str) -> PDFDocument | None:
        mongo_doc = await self._collection.find_one({"_id": ObjectId(pdf_id)})
        return mongo_to_domain(mongo_doc) if mongo_doc else None

    async def update(self, pdf_id: str, update_data: dict) -> bool:
        result = await self._collection.update_one(
            {"_id": ObjectId(pdf_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete(self, pdf_id: str) -> bool:
        result = await self._collection.delete_one({"_id": ObjectId(pdf_id)})
        return result.deleted_count > 0

    async def get_all(self) -> list[PDFDocument]:
        documents = []
        async for mongo_doc in self._collection.find():
            documents.append(mongo_to_domain(mongo_doc))
        return documents

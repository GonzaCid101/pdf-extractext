"""Tests para operaciones CRUD del repositorio PDF."""

from bson import ObjectId

from app.repository.pdf_repository import PDFRepository


class TestPDFRepository:
    async def test_save_pdf_inserts_document(self, mongo_client, pdf_collection):
        document = {
            "filename": "test.pdf",
            "extracted_text": "texto extraído",
            "checksum": "abc123",
        }
        repository = PDFRepository(mongo_client)
        inserted_id = await repository.save(document)

        assert isinstance(inserted_id, str)

        found = await pdf_collection.find_one({"_id": ObjectId(inserted_id)})
        assert found is not None
        assert found["filename"] == "test.pdf"

    async def test_find_by_checksum_returns_document(
        self, mongo_client, pdf_collection
    ):
        document = {
            "filename": "test.pdf",
            "extracted_text": "texto",
            "checksum": "duplicate_checksum",
        }
        await pdf_collection.insert_one(document)

        repository = PDFRepository(mongo_client)
        result = await repository.find_by_checksum("duplicate_checksum")

        assert result is not None
        assert result["checksum"] == "duplicate_checksum"
        assert result["filename"] == "test.pdf"

    async def test_find_by_checksum_returns_none(self, mongo_client, pdf_collection):
        repository = PDFRepository(mongo_client)
        result = await repository.find_by_checksum("nonexistent_checksum")

        assert result is None

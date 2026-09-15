"""Tests para operaciones CRUD del repositorio PDF."""

from bson import ObjectId

from app.domain.pdf_document import PDFDocument
from app.repository.pdf_repository import PDFRepository


class TestPDFRepository:
    async def test_save_pdf_inserts_document(self, mongo_client, pdf_collection):
        document = PDFDocument(
            id="",
            filename="test.pdf",
            extracted_text="texto extraído",
            checksum="abc123",
        )
        repository = PDFRepository(mongo_client)
        inserted_id = await repository.save(document)

        assert isinstance(inserted_id, str)

        found = await pdf_collection.find_one({"_id": ObjectId(inserted_id)})
        assert found is not None
        assert found["filename"] == "test.pdf"

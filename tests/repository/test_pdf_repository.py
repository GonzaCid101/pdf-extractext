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

    async def test_find_by_id_returns_document(self, mongo_client, pdf_collection):
        result = await pdf_collection.insert_one(
            {
                "filename": "test.pdf",
                "extracted_text": "texto",
                "checksum": "find_id_checksum",
            }
        )

        repository = PDFRepository(mongo_client)
        document = await repository.find_by_id(str(result.inserted_id))

        assert document is not None
        assert document.id == str(result.inserted_id)
        assert document.filename == "test.pdf"
        assert document.checksum == "find_id_checksum"

    async def test_find_by_id_returns_none(self, mongo_client, pdf_collection):
        repository = PDFRepository(mongo_client)
        document = await repository.find_by_id(str(ObjectId()))

        assert document is None

    async def test_get_all_returns_list_of_documents(self, mongo_client, pdf_collection):
        await pdf_collection.insert_many(
            [
                {"filename": "doc1.pdf", "extracted_text": "uno", "checksum": "c1"},
                {"filename": "doc2.pdf", "extracted_text": "dos", "checksum": "c2"},
            ]
        )

        repository = PDFRepository(mongo_client)
        documents = await repository.get_all()

        assert len(documents) == 2
        assert all(isinstance(doc, PDFDocument) for doc in documents)
        filenames = {doc.filename for doc in documents}
        assert filenames == {"doc1.pdf", "doc2.pdf"}

    async def test_get_all_returns_empty_list(self, mongo_client, pdf_collection):
        repository = PDFRepository(mongo_client)
        documents = await repository.get_all()

        assert documents == []

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

    async def test_update_existing_document_returns_true_and_updates_fields(
        self, mongo_client, pdf_collection
    ):
        # Arrange
        result = await pdf_collection.insert_one(
            {
                "filename": "original.pdf",
                "extracted_text": "texto original",
                "checksum": "update_checksum",
            }
        )
        document_id = str(result.inserted_id)

        # Act
        repository = PDFRepository(mongo_client)
        updated = await repository.update(document_id, {"filename": "renombrado.pdf"})

        # Assert
        assert updated is True
        found = await pdf_collection.find_one({"_id": ObjectId(document_id)})
        assert found["filename"] == "renombrado.pdf"
        assert found["extracted_text"] == "texto original"
        assert found["checksum"] == "update_checksum"

    async def test_update_nonexistent_document_returns_false(
        self, mongo_client, pdf_collection
    ):
        # Arrange
        repository = PDFRepository(mongo_client)

        # Act
        updated = await repository.update(str(ObjectId()), {"filename": "nada.pdf"})

        # Assert
        assert updated is False

    async def test_delete_existing_document_returns_true_and_removes_it(
        self, mongo_client, pdf_collection
    ):
        # Arrange
        result = await pdf_collection.insert_one(
            {
                "filename": "borrar.pdf",
                "extracted_text": "texto a eliminar",
                "checksum": "delete_checksum",
            }
        )
        document_id = str(result.inserted_id)

        # Act
        repository = PDFRepository(mongo_client)
        deleted = await repository.delete(document_id)

        # Assert
        assert deleted is True
        found = await pdf_collection.find_one({"_id": ObjectId(document_id)})
        assert found is None

    async def test_delete_nonexistent_document_returns_false(
        self, mongo_client, pdf_collection
    ):
        # Arrange
        repository = PDFRepository(mongo_client)

        # Act
        deleted = await repository.delete(str(ObjectId()))

        # Assert
        assert deleted is False
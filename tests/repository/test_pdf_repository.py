"""Tests para operaciones CRUD del repositorio PDF."""

import pytest
from bson import ObjectId

from app.repository.pdf_repository import find_by_checksum, save_pdf


class TestPDFRepository:
    """Tests para operaciones CRUD de PDFs."""

    async def test_save_pdf_inserts_document(self, mongo_client, pdf_collection):
        """Guarda un documento PDF y retorna su ID."""
        document = {
            "filename": "test.pdf",
            "extracted_text": "texto extraído",
            "checksum": "abc123",
        }
        inserted_id = await save_pdf(mongo_client, document)

        assert isinstance(inserted_id, str)

        found = await pdf_collection.find_one({"_id": ObjectId(inserted_id)})
        assert found is not None
        assert found["filename"] == "test.pdf"

    async def test_find_by_checksum_returns_document(
        self, mongo_client, pdf_collection
    ):
        """Encuentra documento por checksum existente."""
        document = {
            "filename": "test.pdf",
            "extracted_text": "texto",
            "checksum": "duplicate_checksum",
        }
        await pdf_collection.insert_one(document)

        result = await find_by_checksum(mongo_client, "duplicate_checksum")

        assert result is not None
        assert result["checksum"] == "duplicate_checksum"
        assert result["filename"] == "test.pdf"

    async def test_find_by_checksum_returns_none(self, mongo_client, pdf_collection):
        """Retorna None cuando el checksum no existe."""
        result = await find_by_checksum(mongo_client, "nonexistent_checksum")

        assert result is None

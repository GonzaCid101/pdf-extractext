"""Tests para endpoint de subida de PDF."""

from io import BytesIO

import pytest
from bson import ObjectId

from app.services.pdf_service import PDFService
from app.services.checksum import ChecksumService


class TestUploadPDF:
    """Tests para POST /upload-pdf."""

    async def test_upload_pdf_saves_to_database_returns_201(
        self, async_client, mongo_client, pdf_collection, pdf_bytes
    ):
        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("new_document.pdf", BytesIO(pdf_bytes), "application/pdf")},
        )

        assert response.status_code == 201
        data = response.json()
        assert "_id" in data
        assert data["filename"] == "new_document.pdf"

        found = await pdf_collection.find_one({"_id": ObjectId(data["_id"])})
        assert found is not None
        assert found["checksum"] == data["checksum"]

    async def test_upload_duplicate_pdf_returns_409(
        self, async_client, mongo_client, pdf_collection, pdf_bytes
    ):
        checksum = ChecksumService().generate(pdf_bytes)

        await pdf_collection.insert_one(
            {
                "filename": "existing.pdf",
                "extracted_text": "existing text",
                "checksum": checksum,
            }
        )

        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("duplicate.pdf", BytesIO(pdf_bytes), "application/pdf")},
        )

        assert response.status_code == 409
        assert "detail" in response.json()

    async def test_valid_pdf_returns_201_with_extracted_data(
        self, async_client, pdf_collection, pdf_bytes
    ):
        pdf_service = PDFService(pdf_collection)
        expected_text = pdf_service.extract_text(pdf_bytes)

        expected_checksum = ChecksumService().generate(pdf_bytes)

        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("dummy.pdf", BytesIO(pdf_bytes), "application/pdf")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "dummy.pdf"
        assert data["extracted_text"] == expected_text
        assert data["checksum"] == expected_checksum
        assert "_id" in data

    async def test_txt_file_returns_415(self, async_client, pdf_collection):
        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("test.txt", b"texto", "text/plain")},
        )

        assert response.status_code == 415

    async def test_empty_pdf_returns_400(self, async_client, pdf_collection):
        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )

        assert response.status_code == 400

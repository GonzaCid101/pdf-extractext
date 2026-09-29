"""Tests para endpoint de subida de PDF."""

import hashlib
from io import BytesIO


class TestUploadPDF:
    """Tests para POST /upload-pdf."""

    async def test_upload_pdf_saves_to_database_returns_201(
        self, async_client, pdf_collection, pdf_bytes
    ):
        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("new_document.pdf", BytesIO(pdf_bytes), "application/pdf")},
        )

        assert response.status_code == 201
        data = response.json()
        assert "_id" in data
        assert data["filename"] == "new_document.pdf"

        get_response = await async_client.get(f"/pdfs/{data['_id']}")
        assert get_response.status_code == 200
        persisted = get_response.json()
        assert persisted["_id"] == data["_id"]
        assert persisted["checksum"] == data["checksum"]

    async def test_upload_duplicate_pdf_returns_409(
        self, async_client, pdf_collection, pdf_bytes
    ):
        """Sub-issue #43: contrato RFC 9457 para documentos duplicados."""
        checksum = hashlib.sha256(pdf_bytes).hexdigest()

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

        # 1. Código de estado HTTP 409 Conflict
        assert response.status_code == 409

        # 2. Content-Type exacto según RFC 9457
        assert response.headers["Content-Type"].startswith("application/problem+json")

        # 3. Estructura Problem Details (RFC 9457)
        problem = response.json()
        assert problem["type"] == "urn:pdf-extractext:errors:duplicate-pdf"
        assert problem["title"] == "Documento PDF duplicado"
        assert problem["status"] == 409
        assert problem["detail"] == "El documento ya existe en el sistema"

    async def test_valid_pdf_returns_201_with_extracted_data(
        self, async_client, pdf_collection, pdf_bytes, pdf_text_content
    ):
        expected_checksum = hashlib.sha256(pdf_bytes).hexdigest()

        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("dummy.pdf", BytesIO(pdf_bytes), "application/pdf")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "dummy.pdf"
        for expected_fragment in pdf_text_content:
            assert expected_fragment in data["extracted_text"]
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

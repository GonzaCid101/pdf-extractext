from io import BytesIO

import pytest


class TestIntegrationFlow:
    async def test_complete_pdf_lifecycle(
        self, async_client, pdf_collection, pdf_bytes
    ):
        response_upload = await async_client.post(
            "/upload-pdf",
            files={"file": ("lifecycle.pdf", BytesIO(pdf_bytes), "application/pdf")},
        )

        assert response_upload.status_code == 201
        data = response_upload.json()
        pdf_id = data["_id"]
        assert data["filename"] == "lifecycle.pdf"

        response_get = await async_client.get(f"/pdfs/{pdf_id}")
        assert response_get.status_code == 200
        assert response_get.json()["_id"] == pdf_id

        response_update = await async_client.patch(
            f"/pdfs/{pdf_id}",
            json={"filename": "updated_lifecycle.pdf"},
        )
        assert response_update.status_code == 200
        assert response_update.json()["filename"] == "updated_lifecycle.pdf"

        response_delete = await async_client.delete(f"/pdfs/{pdf_id}")
        assert response_delete.status_code == 204

        response_verify = await async_client.get(f"/pdfs/{pdf_id}")
        assert response_verify.status_code == 404


class TestEdgeCasesAndRobustness:
    async def test_upload_invalid_format_txt_returns_415(
        self, async_client, pdf_collection
    ):
        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("fake.pdf", b"Este no es un pdf", "text/plain")},
        )
        assert response.status_code == 415

    async def test_upload_corrupt_payload_missing_filename(
        self, async_client, pdf_collection
    ):
        response = await async_client.post(
            "/upload-pdf",
            data={"file": ("", b"random data")},
        )
        assert response.status_code == 422

    async def test_upload_heavy_file_exceeds_limit(self, async_client, pdf_collection):
        large_bytes = b"%PDF" + b"A" * (51 * 1024 * 1024)
        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("heavy.pdf", BytesIO(large_bytes), "application/pdf")},
        )
        assert response.status_code in {400, 413}

    async def test_patch_invalid_payload_returns_422(
        self, async_client, pdf_collection
    ):
        response = await async_client.patch(
            "/pdfs/65797e91c185b4c7c5a93a1b", json={"invalid": "data"}
        )
        assert response.status_code == 422

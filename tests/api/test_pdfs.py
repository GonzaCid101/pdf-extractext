"""Tests de integración para endpoints de gestión de PDFs."""

from bson import ObjectId


class TestGetPDFs:

    async def test_get_all_pdfs(self, async_client, pdf_collection):
        pdf_document = {
            "filename": "test_document.pdf",
            "extracted_text": "Este es el texto extraído del PDF",
            "checksum": "abc123checksum",
        }
        result = await pdf_collection.insert_one(pdf_document)
        inserted_id = str(result.inserted_id)

        response = await async_client.get("/pdfs")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["_id"] == inserted_id
        assert data[0]["filename"] == "test_document.pdf"

    async def test_get_pdf_by_id(self, async_client, pdf_collection):
        specific_id = ObjectId("65797e91c185b4c7c5a93a1b")
        pdf_document = {
            "_id": specific_id,
            "filename": "specific_document.pdf",
            "extracted_text": "Texto del documento específico",
            "checksum": "xyz789checksum",
        }
        await pdf_collection.insert_one(pdf_document)

        response = await async_client.get(f"/pdfs/{specific_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["_id"] == str(specific_id)
        assert data["filename"] == "specific_document.pdf"

    async def test_get_pdf_not_found(self, async_client, pdf_collection):
        non_existent_id = "65797e91c185b4c7c5a93a99"

        response = await async_client.get(f"/pdfs/{non_existent_id}")

        assert response.status_code == 404
        assert "detail" in response.json()


class TestPatchPDF:
    """Tests para PATCH /pdfs/{id} - Actualización de metadatos."""

    async def test_patch_pdf_updates_filename_successfully(
        self, async_client, pdf_collection
    ):

        pdf_document = {
            "filename": "original.pdf",
            "extracted_text": "Texto original del documento",
            "checksum": "abc123checksum",
        }
        result = await pdf_collection.insert_one(pdf_document)
        pdf_id = str(result.inserted_id)

        update_data = {"filename": "updated_document.pdf"}
        response = await async_client.patch(f"/pdfs/{pdf_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "updated_document.pdf"
        assert data["extracted_text"] == "Texto original del documento"
        assert data["checksum"] == "abc123checksum"

    async def test_patch_pdf_not_found_returns_404(self, async_client, pdf_collection):

        non_existent_id = "65797e91c185b4c7c5a93a99"

        update_data = {"filename": "new_name.pdf"}
        response = await async_client.patch(
            f"/pdfs/{non_existent_id}", json=update_data
        )

        assert response.status_code == 404
        assert "detail" in response.json()


class TestDeletePDF:

    async def test_delete_pdf_removes_document_successfully(
        self, async_client, pdf_collection
    ):
        pdf_document = {
            "filename": "to_delete.pdf",
            "extracted_text": "Texto a eliminar",
            "checksum": "delete123checksum",
        }
        result = await pdf_collection.insert_one(pdf_document)
        pdf_id = str(result.inserted_id)

        response = await async_client.delete(f"/pdfs/{pdf_id}")

        assert response.status_code == 204

        get_response = await async_client.get(f"/pdfs/{pdf_id}")
        assert get_response.status_code == 404

    async def test_delete_pdf_not_found_returns_404(self, async_client, pdf_collection):
        
        non_existent_id = "65797e91c185b4c7c5a93a99"

        response = await async_client.delete(f"/pdfs/{non_existent_id}")

        assert response.status_code == 404
        assert "detail" in response.json()

class TestInvalidObjectId:
    """Issue #94: IDs malformados deben devolver 400 con RFC 9457, nunca 500."""

    async def test_get_pdf_with_malformed_id_does_not_raise_500(
        self, async_client
    ):
        response = await async_client.get("/pdfs/abc")

        assert response.status_code != 500

    async def test_get_pdf_with_malformed_id_returns_400(self, async_client):
        response = await async_client.get("/pdfs/abc")

        assert response.status_code == 400

    async def test_malformed_id_returns_rfc9457_problem_json(self, async_client):
        response = await async_client.get("/pdfs/abc")

        assert response.headers["content-type"].startswith(
            "application/problem+json"
        )
        problem = response.json()
        assert problem["status"] == 400
        for field in ("type", "title", "detail", "instance"):
            assert field in problem

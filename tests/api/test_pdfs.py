"""Tests de integración para endpoints GET /pdfs y GET /pdfs/{id}."""

from bson import ObjectId


class TestGetPDFs:
    """Tests para GET /pdfs y GET /pdfs/{id}."""

    async def test_get_all_pdfs(self, async_client, pdf_collection):
        """Retorna todos los documentos PDF guardados."""
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
        """Retorna un documento PDF específico por su ID."""
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
        """Retorna 404 si el ID no existe."""
        non_existent_id = "65797e91c185b4c7c5a93a99"

        response = await async_client.get(f"/pdfs/{non_existent_id}")

        assert response.status_code == 404
        assert "detail" in response.json()

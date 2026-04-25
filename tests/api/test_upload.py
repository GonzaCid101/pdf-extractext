"""Tests para endpoint de subida de PDF."""

from app.services.checksum import generate_checksum
from app.services.pdf_service import extract_text_from_pdf


class TestUploadPDF:
    """Tests para POST /upload-pdf."""

    def test_valid_pdf_returns_200_with_data(self, test_client, pdf_bytes):
        """PDF válido retorna 200 con datos extraídos."""
        expected_text = extract_text_from_pdf(pdf_bytes)
        expected_checksum = generate_checksum(pdf_bytes)
        files = {"file": ("dummy.pdf", pdf_bytes, "application/pdf")}

        response = test_client.post("/upload-pdf", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "dummy.pdf"
        assert data["extracted_text"] == expected_text
        assert data["checksum"] == expected_checksum

    def test_txt_file_returns_415(self, test_client):
        """Archivo no-PDF retorna 415."""
        files = {"file": ("test.txt", b"texto", "text/plain")}

        response = test_client.post("/upload-pdf", files=files)

        assert response.status_code == 415

    def test_empty_pdf_returns_400(self, test_client):
        """PDF vacío retorna 400."""
        files = {"file": ("empty.pdf", b"", "application/pdf")}

        response = test_client.post("/upload-pdf", files=files)

        assert response.status_code == 400

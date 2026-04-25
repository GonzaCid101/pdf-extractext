"""Tests para servicio de extracción de PDF."""

from app.services.pdf_service import extract_text_from_pdf


class TestExtractTextFromPDF:
    """Tests para extract_text_from_pdf."""

    def test_returns_string(self, pdf_bytes):
        """Retorna string."""
        result = extract_text_from_pdf(pdf_bytes)

        assert isinstance(result, str)

    def test_returns_non_empty_text(self, pdf_bytes):
        """Retorna texto no vacío."""
        result = extract_text_from_pdf(pdf_bytes)

        assert len(result) > 0

    def test_contains_expected_content(self, pdf_bytes, pdf_text_content):
        """Contiene contenido esperado."""
        result = extract_text_from_pdf(pdf_bytes)

        for expected in pdf_text_content:
            assert expected in result

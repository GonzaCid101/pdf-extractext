"""Tests para servicio de extracción de PDF."""

from app.services.pdf_service import PDFService
from unittest.mock import AsyncMock
from app.repository.pdf_repository import PDFRepository


class TestPDFService:
    """Tests para PDFService."""

    def test_extract_text_returns_string(self, pdf_bytes):
        result = PDFService(PDFRepository(AsyncMock())).extract_text(pdf_bytes)
        assert isinstance(result, str)

    def test_extract_text_returns_non_empty(self, pdf_bytes):
        result = PDFService(PDFRepository(AsyncMock())).extract_text(pdf_bytes)
        assert len(result) > 0

    def test_extract_text_contains_expected_content(self, pdf_bytes, pdf_text_content):
        result = PDFService(PDFRepository(AsyncMock())).extract_text(pdf_bytes)

        for expected in pdf_text_content:
            assert expected in result

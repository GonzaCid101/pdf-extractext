"""Tests para servicio de extracción de PDF."""

import pytest

from app.services.pdf_service import PDFService
from tests.fakes import FakePDFRepository


@pytest.fixture
def pdf_service() -> PDFService:
    """Servicio con repositorio en memoria reutilizado por los tests."""
    return PDFService(FakePDFRepository())


class TestPDFService:
    """Tests para PDFService."""

    def test_extract_text_returns_string(self, pdf_bytes, pdf_service):
        result = pdf_service.extract_text(pdf_bytes)
        assert isinstance(result, str)

    def test_extract_text_returns_non_empty(self, pdf_bytes, pdf_service):
        result = pdf_service.extract_text(pdf_bytes)
        assert len(result) > 0

    def test_extract_text_contains_expected_content(
        self, pdf_bytes, pdf_text_content, pdf_service
    ):
        result = pdf_service.extract_text(pdf_bytes)

        for expected in pdf_text_content:
            assert expected in result

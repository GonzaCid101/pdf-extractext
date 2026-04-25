"""Tests para modelos de datos PDF."""

import pytest
from pydantic import ValidationError

from app.models.pdf_models import PDFDocumentResponse


class TestPDFDocumentResponse:
    """Tests para PDFDocumentResponse."""

    def test_requires_filename(self):
        """Requiere filename."""
        with pytest.raises(ValidationError):
            PDFDocumentResponse(extracted_text="texto", checksum="abc")

    def test_requires_extracted_text(self):
        """Requiere extracted_text."""
        with pytest.raises(ValidationError):
            PDFDocumentResponse(filename="doc.pdf", checksum="abc")

    def test_requires_checksum(self):
        """Requiere checksum."""
        with pytest.raises(ValidationError):
            PDFDocumentResponse(filename="doc.pdf", extracted_text="texto")

    def test_accepts_valid_data(self):
        """Acepta datos válidos."""
        doc = PDFDocumentResponse(
            filename="doc.pdf",
            extracted_text="contenido",
            checksum="a1b2",
        )

        assert doc.filename == "doc.pdf"
        assert doc.extracted_text == "contenido"
        assert doc.checksum == "a1b2"

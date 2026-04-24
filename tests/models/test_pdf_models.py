"""Tests para modelos de datos PDF."""

import pytest
from pydantic import ValidationError

from app.models.pdf_models import PDFDocumentResponse


class TestPDFDocumentResponse:
    """Tests para el modelo de respuesta de documento PDF."""

    def test_modelo_requiere_filename(self):
        with pytest.raises(ValidationError):
            PDFDocumentResponse(extracted_text="contenido", checksum="abc123")

    def test_modelo_requiere_extracted_text(self):
        with pytest.raises(ValidationError):
            PDFDocumentResponse(filename="doc.pdf", checksum="abc123")

    def test_modelo_requiere_checksum(self):
        with pytest.raises(ValidationError):
            PDFDocumentResponse(filename="doc.pdf", extracted_text="contenido")

    def test_modelo_acepta_datos_validos(self):
        doc = PDFDocumentResponse(
            filename="documento.pdf",
            extracted_text="Este es el contenido extraído",
            checksum="a1b2c3d4e5f6",
        )
        assert doc.filename == "documento.pdf"
        assert doc.extracted_text == "Este es el contenido extraído"
        assert doc.checksum == "a1b2c3d4e5f6"

"""Tests para modelos de datos PDF."""

import pytest
from pydantic import ValidationError

from app.models.pdf_models import PDFDocumentResponse


class TestPDFDocumentResponse:
    """Tests para PDFDocumentResponse."""

    def test_requires_filename(self):
        """Requiere filename."""
        with pytest.raises(ValidationError):
            PDFDocumentResponse(id="abc123", extracted_text="texto", checksum="abc")

    def test_requires_extracted_text(self):
        """Requiere extracted_text."""
        with pytest.raises(ValidationError):
            PDFDocumentResponse(id="abc123", filename="doc.pdf", checksum="abc")

    def test_requires_checksum(self):
        """Requiere checksum."""
        with pytest.raises(ValidationError):
            PDFDocumentResponse(id="abc123", filename="doc.pdf", extracted_text="texto")

    def test_accepts_valid_data(self):
        """Acepta datos válidos."""
        doc = PDFDocumentResponse(
            id="507f1f77bcf86cd799439011",
            filename="doc.pdf",
            extracted_text="contenido",
            checksum="a1b2",
        )

        assert doc.id == "507f1f77bcf86cd799439011"
        assert doc.filename == "doc.pdf"
        assert doc.extracted_text == "contenido"
        assert doc.checksum == "a1b2"


class TestPDFDocumentResponseDesacopladoDeMongoDB:
    """Issue #49: el DTO expone `id` y no conoce el `_id` de MongoDB."""

    # FASE RED: Este test fallará inicialmente
    def test_serializa_el_identificador_con_la_clave_id(self):
        """La representación serializada usa `id`, nunca `_id`."""
        response = PDFDocumentResponse(
            id="507f1f77bcf86cd799439011",
            filename="doc.pdf",
            extracted_text="contenido",
            checksum="a1b2",
        )

        # by_alias=True replica la serialización que FastAPI aplica al response_model
        payload = response.model_dump(by_alias=True)

        assert payload["id"] == "507f1f77bcf86cd799439011"
        assert "_id" not in payload

    # FASE RED: Este test fallará inicialmente
    def test_no_admite_el_identificador_de_mongodb_como_entrada(self):
        """`_id` no es un nombre de entrada válido: el único identificador es `id`."""
        with pytest.raises(ValidationError):
            PDFDocumentResponse(
                _id="507f1f77bcf86cd799439011",
                filename="doc.pdf",
                extracted_text="contenido",
                checksum="a1b2",
            )

    # FASE RED: Este test fallará inicialmente
    def test_el_esquema_publico_no_expone_el_campo_de_mongodb(self):
        """El esquema OpenAPI declara `id` y omite `_id`."""
        properties = PDFDocumentResponse.model_json_schema()["properties"]

        assert "id" in properties
        assert "_id" not in properties

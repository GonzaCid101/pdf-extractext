"""Tests del mapper de la capa API: entidad de dominio → DTO de respuesta."""

from app.api.mappers import to_pdf_document_response
from app.domain.pdf_document import PDFDocument
from app.models.pdf_models import PDFDocumentResponse


class TestToPDFDocumentResponse:
    """Tests para el mapper de la capa API."""

    # FASE RED: Este test fallará inicialmente
    def test_mapea_cada_campo_del_documento_al_dto(self):
        """El DTO de respuesta refleja los valores del documento de dominio."""
        document = PDFDocument(
            id="507f1f77bcf86cd799439011",
            filename="doc.pdf",
            extracted_text="contenido",
            checksum="a1b2",
        )

        response = to_pdf_document_response(document)

        assert isinstance(response, PDFDocumentResponse)
        assert response.id == "507f1f77bcf86cd799439011"
        assert response.filename == "doc.pdf"
        assert response.extracted_text == "contenido"
        assert response.checksum == "a1b2"

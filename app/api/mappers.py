"""Traducción de la entidad de dominio al DTO de respuesta de la API."""

from app.domain.pdf_document import PDFDocument
from app.models.pdf_models import PDFDocumentResponse


def to_pdf_document_response(document: PDFDocument) -> PDFDocumentResponse:
    return PDFDocumentResponse(
        id=document.id,
        filename=document.filename,
        extracted_text=document.extracted_text,
        checksum=document.checksum,
    )

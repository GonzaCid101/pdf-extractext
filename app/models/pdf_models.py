"""Modelos de datos para documentos PDF."""

from pydantic import BaseModel


class PDFDocumentResponse(BaseModel):
    """Modelo de respuesta para un documento PDF procesado."""

    filename: str
    extracted_text: str
    checksum: str

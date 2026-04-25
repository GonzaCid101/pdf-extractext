"""Modelos Pydantic para documentos PDF."""

from pydantic import BaseModel


class PDFDocumentResponse(BaseModel):
    """Respuesta de documento PDF procesado."""

    filename: str
    extracted_text: str
    checksum: str

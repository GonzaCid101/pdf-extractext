"""Modelos Pydantic para documentos PDF."""

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class PDFDocumentResponse(BaseModel):
    """Respuesta de documento PDF procesado."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    filename: str
    extracted_text: str
    checksum: str


class PDFUpdateRequest(BaseModel):
    """Solicitud de actualización de metadatos PDF.

    Solo permite actualizar el filename. Los campos checksum y extracted_text
    son inmutables para mantener la integridad del documento.
    """

    model_config = ConfigDict(extra="forbid")

    filename: Optional[str] = Field(
        default=None,
        description="Nuevo nombre del archivo PDF",
        examples=["documento_actualizado.pdf"],
    )

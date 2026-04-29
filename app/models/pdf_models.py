"""Modelos Pydantic para documentos PDF."""

from pydantic import BaseModel, Field, ConfigDict


class PDFDocumentResponse(BaseModel):
    """Respuesta de documento PDF procesado."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    filename: str
    extracted_text: str
    checksum: str

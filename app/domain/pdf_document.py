"""Entidad de dominio para un documento PDF."""

from dataclasses import dataclass


@dataclass
class PDFDocument:
    id: str
    filename: str
    extracted_text: str
    checksum: str

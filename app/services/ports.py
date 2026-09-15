"""Ports: contratos que los casos de uso necesitan de la persistencia."""

from typing import Protocol

from app.domain.pdf_document import PDFDocument


class PDFRepositoryPort(Protocol):
    async def save(self, document: PDFDocument) -> str: ...

    async def find_by_checksum(self, checksum: str) -> PDFDocument | None: ...

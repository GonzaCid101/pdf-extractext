"""Ports: contratos que los casos de uso necesitan de la persistencia."""

from typing import Protocol

from app.domain.pdf_document import PDFDocument


class PDFRepositoryPort(Protocol):
    async def save(self, document: PDFDocument) -> str: ...

    async def find_by_id(self, pdf_id: str) -> PDFDocument | None: ...

    async def get_all(self, skip: int = 0, limit: int = 50) -> list[PDFDocument]: ...

    async def update(self, pdf_id: str, update_data: dict) -> bool: ...

    async def delete(self, pdf_id: str) -> bool: ...

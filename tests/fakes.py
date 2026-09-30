"""Implementaciones falsas (in-memory) para tests de servicios."""

import hashlib

from app.domain.exceptions import DuplicatePDFError
from app.domain.pdf_document import PDFDocument


class FakePDFRepository:
    def __init__(self) -> None:
        self._documents: dict[str, PDFDocument] = {}

    async def save(self, document: PDFDocument) -> str:
        if any(doc.checksum == document.checksum for doc in self._documents.values()):
            raise DuplicatePDFError("Document with same checksum already exists")
        document.id = (
            f"fake-{hashlib.sha256(document.checksum.encode()).hexdigest()[:12]}"
        )
        self._documents[document.id] = document
        return document.id

    async def find_by_checksum(self, checksum: str) -> PDFDocument | None:
        return next(
            (doc for doc in self._documents.values() if doc.checksum == checksum),
            None,
        )

    # Métodos de apoyo para verificaciones en tests
    def saved_documents(self) -> list[PDFDocument]:
        return list(self._documents.values())

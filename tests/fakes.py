"""Implementaciones falsas (in-memory) para tests de servicios."""

from app.domain.exceptions import DuplicatePDFError
from app.domain.pdf_document import PDFDocument


class FakePDFRepository:
    """Fake in-memory que implementa el contrato completo del puerto."""

    def __init__(self) -> None:
        self._documents: dict[str, PDFDocument] = {}
        self._counter = 0

    async def save(self, document: PDFDocument) -> str:
        # Emula el índice único de checksum en MongoDB
        if any(
            doc.checksum == document.checksum for doc in self._documents.values()
        ):
            raise DuplicatePDFError("Document with same checksum already exists")

        self._counter += 1
        document.id = f"fake-id-{self._counter}"
        self._documents[document.id] = document
        return document.id

    async def find_by_id(self, pdf_id: str) -> PDFDocument | None:
        return self._documents.get(pdf_id)

    async def find_by_checksum(self, checksum: str) -> PDFDocument | None:
        return next(
            (doc for doc in self._documents.values() if doc.checksum == checksum),
            None,
        )

    async def get_all(self, skip: int = 0, limit: int = 50) -> list[PDFDocument]:
        return list(self._documents.values())[skip : skip + limit]

    async def update(self, pdf_id: str, update_data: dict) -> bool:
        document = self._documents.get(pdf_id)
        if document is None:
            return False
        if "filename" in update_data:
            document.filename = update_data["filename"]
        return True

    async def delete(self, pdf_id: str) -> bool:
        return self._documents.pop(pdf_id, None) is not None

    def saved_documents(self) -> list[PDFDocument]:
        return list(self._documents.values())

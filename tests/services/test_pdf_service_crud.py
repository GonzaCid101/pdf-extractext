"""Tests unitarios del CRUD de PDFService contra el puerto PDFRepositoryPort."""

import pytest

# FASE RED: Este test fallará inicialmente
from app.domain.exceptions import DuplicatePDFError, PDFNotFoundError
from app.domain.pdf_document import PDFDocument
from app.services.checksum import ChecksumService
from app.services.pdf_service import PDFService


class InMemoryPDFRepository:
    """Fake in-memory que implementa el contrato completo del puerto."""

    def __init__(self) -> None:
        self._docs: dict[str, PDFDocument] = {}
        self._counter = 0

    async def save(self, document: PDFDocument) -> str:
        # Emula el índice único de checksum en MongoDB
        if any(d.checksum == document.checksum for d in self._docs.values()):
            raise DuplicatePDFError("Document with same checksum already exists")
        self._counter += 1
        new_id = f"fake-id-{self._counter}"
        document.id = new_id
        self._docs[new_id] = document
        return new_id

    async def find_by_id(self, pdf_id: str) -> PDFDocument | None:
        return self._docs.get(pdf_id)

    async def get_all(self) -> list[PDFDocument]:
        return list(self._docs.values())

    async def update(self, pdf_id: str, update_data: dict) -> bool:
        doc = self._docs.get(pdf_id)
        if doc is None:
            return False
        if "filename" in update_data:
            doc.filename = update_data["filename"]
        return True

    async def delete(self, pdf_id: str) -> bool:
        return self._docs.pop(pdf_id, None) is not None


def _build_service() -> PDFService:
    return PDFService(InMemoryPDFRepository(), ChecksumService())


async def _seed(service: PDFService, filename: str = "doc.pdf") -> PDFDocument:
    repo = service._repository
    document = PDFDocument(
        id="",
        filename=filename,
        extracted_text="texto de prueba",
        checksum=f"checksum-{filename}",
    )
    document.id = await repo.save(document)
    return document


class TestGetAll:

    async def test_returns_empty_list_when_no_documents(self):
        service = _build_service()

        documents = await service.get_all()

        assert documents == []

    async def test_returns_all_saved_documents(self):
        service = _build_service()
        await _seed(service, "uno.pdf")
        await _seed(service, "dos.pdf")

        documents = await service.get_all()

        assert len(documents) == 2
        assert {d.filename for d in documents} == {"uno.pdf", "dos.pdf"}


class TestGetById:

    async def test_returns_document_when_exists(self):
        service = _build_service()
        saved = await _seed(service)

        document = await service.get_by_id(saved.id)

        assert document.id == saved.id
        assert document.filename == "doc.pdf"

    async def test_raises_not_found_when_missing(self):
        service = _build_service()

        with pytest.raises(PDFNotFoundError):
            await service.get_by_id("id-inexistente")


class TestUpdateFilename:

    async def test_updates_filename_and_returns_document(self):
        service = _build_service()
        saved = await _seed(service)

        updated = await service.update_filename(saved.id, "renombrado.pdf")

        assert updated.filename == "renombrado.pdf"
        assert updated.id == saved.id

    async def test_preserves_checksum_and_extracted_text(self):
        service = _build_service()
        saved = await _seed(service)

        updated = await service.update_filename(saved.id, "renombrado.pdf")

        assert updated.checksum == saved.checksum
        assert updated.extracted_text == saved.extracted_text

    async def test_raises_not_found_when_missing(self):
        service = _build_service()

        with pytest.raises(PDFNotFoundError):
            await service.update_filename("id-inexistente", "nuevo.pdf")


class TestDelete:

    async def test_removes_document(self):
        service = _build_service()
        saved = await _seed(service)

        await service.delete(saved.id)

        with pytest.raises(PDFNotFoundError):
            await service.get_by_id(saved.id)

    async def test_raises_not_found_when_missing(self):
        service = _build_service()

        with pytest.raises(PDFNotFoundError):
            await service.delete("id-inexistente")

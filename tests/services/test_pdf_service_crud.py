"""Tests unitarios del CRUD de PDFService contra el puerto PDFRepositoryPort."""

import pytest

# FASE RED: Este test fallará inicialmente
from app.domain.exceptions import PDFNotFoundError
from app.domain.pdf_document import PDFDocument
from app.services.pdf_service import PDFService
from tests.fakes import FakePDFRepository


def _build_service() -> PDFService:
    return PDFService(FakePDFRepository())


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

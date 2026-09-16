"""Tests del contrato de PDFService.process_and_save con repositorio en memoria."""

import pytest

from app.domain.pdf_document import PDFDocument
from app.services.checksum import ChecksumService
from app.services.pdf_service import DuplicatePDFError, PDFService
from app.services.ports import DuplicateRecordError


class InMemoryPDFRepository:
    def __init__(self):
        self.saved: list[PDFDocument] = []

    async def save(self, document: PDFDocument) -> str:
        # Emula el índice único de checksum en MongoDB
        if any(d.checksum == document.checksum for d in self.saved):
            raise DuplicateRecordError("Document with same checksum already exists")
        self.saved.append(document)
        return "65f1a2b3c4d5e6f7a8b9c0d1"


class TestProcessAndSave:

    async def test_returns_domain_entity(self, pdf_bytes):
        service = PDFService(InMemoryPDFRepository(), ChecksumService())

        result = await service.process_and_save("informe.pdf", pdf_bytes)

        assert isinstance(result, PDFDocument)
        assert result.filename == "informe.pdf"
        assert result.extracted_text == service.extract_text(pdf_bytes)
        assert result.checksum == ChecksumService().generate(pdf_bytes)
        assert result.id == "65f1a2b3c4d5e6f7a8b9c0d1"

    async def test_raises_duplicate_error_on_existing_checksum(self, pdf_bytes):
        service = PDFService(InMemoryPDFRepository(), ChecksumService())
        await service.process_and_save("original.pdf", pdf_bytes)

        with pytest.raises(DuplicatePDFError):
            await service.process_and_save("copia.pdf", pdf_bytes)

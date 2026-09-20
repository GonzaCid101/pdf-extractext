"""Tests del contrato de PDFService.process_and_save con repositorio en memoria."""

import hashlib

import pytest

from app.domain.exceptions import DuplicatePDFError
from app.domain.pdf_document import PDFDocument
from app.services.checksum import ChecksumService
from app.services.pdf_service import PDFService
from tests.fakes import FakePDFRepository


class TestProcessAndSave:
    async def test_returns_domain_entity(self, pdf_bytes, pdf_text_content):
        repository = FakePDFRepository()
        service = PDFService(repository, ChecksumService())

        result = await service.process_and_save("informe.pdf", pdf_bytes)

        assert isinstance(result, PDFDocument)
        assert result.filename == "informe.pdf"
        assert result.checksum == hashlib.sha256(pdf_bytes).hexdigest()
        for fragment in pdf_text_content:
            assert fragment in result.extracted_text
        assert result.id
        assert len(repository.saved_documents()) == 1

    async def test_raises_duplicate_error_on_existing_checksum(self, pdf_bytes):
        repository = FakePDFRepository()
        service = PDFService(repository, ChecksumService())
        await service.process_and_save("original.pdf", pdf_bytes)

        with pytest.raises(DuplicatePDFError):
            await service.process_and_save("copia.pdf", pdf_bytes)

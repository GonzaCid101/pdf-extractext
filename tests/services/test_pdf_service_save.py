"""Tests del contrato de PDFService.process_and_save con repositorio en memoria."""

import hashlib

import pytest

from app.domain.exceptions import DuplicatePDFError
from app.domain.pdf_document import PDFDocument
from app.services.pdf_service import PDFService
from tests.fakes import FakePDFRepository


def _checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class TestProcessAndSave:
    async def test_returns_domain_entity(self, pdf_bytes, pdf_text_content):
        repository = FakePDFRepository()
        service = PDFService(repository)
        checksum = _checksum(pdf_bytes)

        result = await service.process_and_save("informe.pdf", pdf_bytes, checksum)

        assert isinstance(result, PDFDocument)
        assert result.filename == "informe.pdf"
        assert result.checksum == checksum
        for fragment in pdf_text_content:
            assert fragment in result.extracted_text
        assert result.id
        assert len(repository.saved_documents()) == 1

    async def test_raises_duplicate_error_on_existing_checksum(self, pdf_bytes):
        repository = FakePDFRepository()
        service = PDFService(repository)
        checksum = _checksum(pdf_bytes)
        await service.process_and_save("original.pdf", pdf_bytes, checksum)

        with pytest.raises(DuplicatePDFError):
            await service.process_and_save("copia.pdf", pdf_bytes, checksum)

    async def test_requires_explicit_checksum(self, pdf_bytes):
        # FASE RED: Este test fallará inicialmente
        repository = FakePDFRepository()
        service = PDFService(repository)

        with pytest.raises(TypeError):
            await service.process_and_save("sin_checksum.pdf", pdf_bytes)

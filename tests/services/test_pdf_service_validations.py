"""Tests de validaciones de dominio en la capa de servicios."""

import pytest

from app.domain.pdf_document import PDFDocument
from app.services.pdf_service import FilenameTooLongError, PDFService

MAX_FILENAME_LENGTH = 100
CHECKSUM = "0" * 64


class InMemoryPDFRepository:
    def __init__(self):
        self.saved: list[PDFDocument] = []

    async def save(self, document: PDFDocument) -> str:
        self.saved.append(document)
        return "65f1a2b3c4d5e6f7a8b9c0d1"

    async def find_by_checksum(self, checksum: str) -> PDFDocument | None:
        return None


class TestFilenameValidation:
    async def test_rejects_filename_longer_than_100_chars(self, pdf_bytes):
        service = PDFService(InMemoryPDFRepository())
        long_filename = "a" * (MAX_FILENAME_LENGTH + 1) + ".pdf"

        with pytest.raises(FilenameTooLongError):
            await service.process_and_save(long_filename, pdf_bytes, CHECKSUM)

    async def test_accepts_filename_of_exactly_100_chars(self, pdf_bytes):
        service = PDFService(InMemoryPDFRepository())
        filename = "a" * (MAX_FILENAME_LENGTH - 4) + ".pdf"

        document = await service.process_and_save(filename, pdf_bytes, CHECKSUM)

        assert document.filename == filename

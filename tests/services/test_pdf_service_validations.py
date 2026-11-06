"""Tests de validaciones de dominio en la capa de servicios."""

import pytest

from app.services.pdf_service import (
    MAX_FILENAME_LENGTH,
    FilenameTooLongError,
    PDFService,
)
from tests.fakes import FakePDFRepository

CHECKSUM = "0" * 64


class TestFilenameValidation:
    async def test_rejects_filename_longer_than_max_length(self, pdf_bytes):
        service = PDFService(FakePDFRepository())
        long_filename = "a" * (MAX_FILENAME_LENGTH + 1) + ".pdf"

        with pytest.raises(FilenameTooLongError):
            await service.process_and_save(long_filename, pdf_bytes, CHECKSUM)

    async def test_accepts_filename_of_exactly_max_length(self, pdf_bytes):
        service = PDFService(FakePDFRepository())
        filename = "a" * (MAX_FILENAME_LENGTH - 4) + ".pdf"

        document = await service.process_and_save(filename, pdf_bytes, CHECKSUM)

        assert document.filename == filename

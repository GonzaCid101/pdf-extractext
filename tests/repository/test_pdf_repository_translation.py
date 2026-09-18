# FASE RED: Este test fallará inicialmente
"""Tests unitarios de la traducción única de errores nativos de MongoDB
a excepciones de dominio en PDFRepository (Sub-issue #41).

No requieren un MongoDB real: usan una colección falsa.
"""

import pytest
from pymongo.errors import DuplicateKeyError

from app.domain.exceptions import DuplicatePDFError
from app.domain.pdf_document import PDFDocument
from app.repository.pdf_repository import PDFRepository


class FakeCollectionRaisesDuplicateKey:
    """Colección falsa que emula el índice único de MongoDB."""

    async def insert_one(self, _doc):
        raise DuplicateKeyError("E11000 duplicate key error")


def _make_repo() -> PDFRepository:
    repo = PDFRepository.__new__(PDFRepository)  # evita tocar settings/cliente real
    repo._collection = FakeCollectionRaisesDuplicateKey()
    return repo


class TestSaveTranslation:
    async def test_duplicate_key_error_se_traduce_a_excepcion_de_dominio(self):
        repo = _make_repo()
        document = PDFDocument(id="", filename="a.pdf", extracted_text="t", checksum="abc")

        with pytest.raises(DuplicatePDFError):
            await repo.save(document)

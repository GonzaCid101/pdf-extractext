"""Tests directos del repositorio para setup_indexes."""

import pytest

from app.domain.exceptions import DuplicatePDFError
from app.domain.pdf_document import PDFDocument
from app.repository.pdf_repository import PDFRepository


class TestSetupIndexes:
    """Tests para PDFRepository.setup_indexes()."""

    # FASE RED: Este test fallará inicialmente
    async def test_setup_indexes_crea_indice_unico_sobre_checksum(
        self, mongo_client, pdf_collection
    ):
        """Tras setup_indexes debe existir un índice único sobre checksum."""
        repo = PDFRepository(mongo_client)

        await repo.setup_indexes()

        indexes = await pdf_collection.index_information()

        checksum_indexes = [
            info
            for name, info in indexes.items()
            if "key" in info and any(key[0] == "checksum" for key in info["key"])
        ]

        assert checksum_indexes, "Debe crearse un índice sobre el campo checksum"
        assert any(
            info.get("unique") is True for info in checksum_indexes
        ), "El índice sobre checksum debe ser único"

    # FASE RED: Este test fallará inicialmente
    async def test_setup_indexes_rechaza_segundo_documento_con_mismo_checksum(
        self, mongo_client, pdf_collection
    ):
        """La violación de unicidad del índice se traduce a DuplicatePDFError."""
        repo = PDFRepository(mongo_client)

        await repo.setup_indexes()

        first_document = PDFDocument(
            id="",
            filename="primer.pdf",
            extracted_text="texto uno",
            checksum="checksum-identico",
        )
        second_document = PDFDocument(
            id="",
            filename="segundo.pdf",
            extracted_text="texto dos",
            checksum="checksum-identico",
        )

        await repo.save(first_document)

        with pytest.raises(DuplicatePDFError):
            await repo.save(second_document)

"""Servicio de extracción y procesamiento de PDFs."""

import fitz

from app.domain.pdf_document import PDFDocument
from app.services.checksum import ChecksumService
from app.services.ports import DuplicateRecordError, PDFRepositoryPort


class DuplicatePDFError(Exception):
    pass


class FilenameTooLongError(ValueError):
    pass


class PDFNotFoundError(Exception):
    pass


class PDFNotFoundError(Exception):
    pass


MAX_FILENAME_LENGTH = 100


class PDFService:
    def __init__(
        self,
        repository: PDFRepositoryPort,
        checksum_service: ChecksumService | None = None,
    ) -> None:
        self._repository = repository
        self._checksum_service = checksum_service or ChecksumService()

    def extract_text(self, pdf_content: bytes) -> str:
        extracted_text = ""
        try:
            with fitz.open(stream=pdf_content, filetype="pdf") as pdf_document:
                for page in pdf_document:
                    extracted_text += page.get_text()
        except Exception as error:
            raise ValueError(f"Contenido PDF inválido: {error}") from error
        return extracted_text

    async def process_and_save(self, filename: str, pdf_content: bytes) -> PDFDocument:
        # FASE GREEN: Implementación mínima para pasar el test
        if len(filename) > MAX_FILENAME_LENGTH:
            raise FilenameTooLongError(
                f"El nombre del archivo excede los {MAX_FILENAME_LENGTH} caracteres"
            )

        document = PDFDocument(
            id="",
            filename=filename,
            extracted_text=self.extract_text(pdf_content),
            checksum=self._checksum_service.generate(pdf_content),
        )

        try:
            document.id = await self._repository.save(document)
        except DuplicateRecordError as error:
            raise DuplicatePDFError("El documento ya existe en el sistema") from error

        return document

    async def get_all(self) -> list[PDFDocument]:
        return await self._repository.get_all()

    async def get_by_id(self, pdf_id: str) -> PDFDocument:
        document = await self._repository.find_by_id(pdf_id)
        if document is None:
            raise PDFNotFoundError(f"PDF con id '{pdf_id}' no encontrado")
        return document

    async def update_filename(self, pdf_id: str, filename: str) -> PDFDocument:
        document = await self.get_by_id(pdf_id)
        await self._repository.update(pdf_id, {"filename": filename})
        document.filename = filename
        return document

    async def delete(self, pdf_id: str) -> None:
        document = await self._repository.find_by_id(pdf_id)
        if document is None:
            raise PDFNotFoundError(f"PDF con id '{pdf_id}' no encontrado")
        await self._repository.delete(pdf_id)

    async def get_all(self) -> list[PDFDocument]:
        return await self._repository.get_all()

    async def get_by_id(self, pdf_id: str) -> PDFDocument:
        document = await self._repository.find_by_id(pdf_id)
        if document is None:
            raise PDFNotFoundError(f"PDF con id '{pdf_id}' no encontrado")
        return document

    async def update_filename(self, pdf_id: str, filename: str) -> PDFDocument:
        document = await self.get_by_id(pdf_id)
        await self._repository.update(pdf_id, {"filename": filename})
        document.filename = filename
        return document

    async def delete(self, pdf_id: str) -> None:
        document = await self._repository.find_by_id(pdf_id)
        if document is None:
            raise PDFNotFoundError(f"PDF con id '{pdf_id}' no encontrado")
        await self._repository.delete(pdf_id)
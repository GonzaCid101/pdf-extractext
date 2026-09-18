"""Servicio de extracción y procesamiento de PDFs."""

import fitz

# FASE GREEN: Implementación mínima para pasar el test
# Las excepciones de dominio se importan; el servicio solo las deja fluir.
from app.domain.exceptions import DuplicatePDFError, PDFNotFoundError
from app.domain.pdf_document import PDFDocument
from app.services.checksum import ChecksumService
from app.services.ports import PDFRepositoryPort

__all__ = ["DuplicatePDFError", "PDFNotFoundError", "FilenameTooLongError", "PDFService"]


class FilenameTooLongError(ValueError):
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

        # El repositorio traduce los errores nativos de Mongo a excepciones
        # de dominio; el servicio no re-traduce, solo deja fluir (KISS).
        document.id = await self._repository.save(document)

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

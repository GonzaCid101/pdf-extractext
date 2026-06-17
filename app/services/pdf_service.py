"""Servicio de extracción y procesamiento de PDFs."""
import fitz
from app.repository.pdf_repository import PDFRepository
from app.services.checksum import ChecksumService
class DuplicatePDFError(Exception):
    pass
class PDFService:
    def __init__(
        self,
        repository: PDFRepository,
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
    async def process_and_save(self, filename: str, pdf_content: bytes) -> dict:
        extracted_text = self.extract_text(pdf_content)
        checksum = self._checksum_service.generate(pdf_content)
        if await self._repository.find_by_checksum(checksum) is not None:
            raise DuplicatePDFError("El documento ya existe en el sistema")
        document = {
            "filename": filename,
            "extracted_text": extracted_text,
            "checksum": checksum,
        }
        document["_id"] = await self._repository.save(document)
        return document
"""Servicio de extracción y procesamiento de PDFs."""

import fitz
from motor.motor_asyncio import AsyncIOMotorClient

from app.repository.pdf_repository import find_by_checksum, save_pdf
from app.services.checksum import generate_checksum


class DuplicatePDFError(Exception):
    """PDF duplicado detectado por checksum."""

    pass


async def process_and_save_pdf(
    db: AsyncIOMotorClient, filename: str, pdf_content: bytes
) -> dict:
    """Procesa PDF y lo guarda en BD. Lanza DuplicatePDFError si existe."""
    extracted_text = extract_text_from_pdf(pdf_content)
    checksum = generate_checksum(pdf_content)

    if await find_by_checksum(db, checksum) is not None:
        raise DuplicatePDFError("El documento ya existe en el sistema")

    document = {
        "filename": filename,
        "extracted_text": extracted_text,
        "checksum": checksum,
    }

    document["_id"] = await save_pdf(db, document)

    return document


def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extrae texto plano de bytes de PDF."""
    extracted_text = ""

    try:
        with fitz.open(stream=pdf_content, filetype="pdf") as pdf_document:
            for page in pdf_document:
                extracted_text += page.get_text()
    except Exception as error:
        raise ValueError(f"Contenido PDF inválido: {error}") from error

    return extracted_text

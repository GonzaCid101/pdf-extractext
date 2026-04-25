"""Servicio de extracción de texto de PDFs."""

import fitz


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

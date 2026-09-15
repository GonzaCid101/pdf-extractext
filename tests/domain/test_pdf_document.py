"""Tests para la entidad de dominio PDFDocument."""

from app.domain.pdf_document import PDFDocument


class TestPDFDocument:

    def test_entity_instantiates_with_required_attributes(self):
        document = PDFDocument(
            id="65f1a2b3c4d5e6f7a8b9c0d1",
            filename="informe.pdf",
            extracted_text="Contenido extraido del PDF",
            checksum="a" * 64,
        )

        assert document.id == "65f1a2b3c4d5e6f7a8b9c0d1"
        assert document.filename == "informe.pdf"
        assert document.extracted_text == "Contenido extraido del PDF"
        assert document.checksum == "a" * 64
        assert all(
            isinstance(value, str)
            for value in (
                document.id,
                document.filename,
                document.extracted_text,
                document.checksum,
            )
        )

    def test_entity_is_mutable(self):
        document = PDFDocument(
            id="65f1a2b3c4d5e6f7a8b9c0d1",
            filename="informe.pdf",
            extracted_text="Contenido extraido del PDF",
            checksum="a" * 64,
        )

        document.filename = "informe_actualizado.pdf"

        assert document.filename == "informe_actualizado.pdf"

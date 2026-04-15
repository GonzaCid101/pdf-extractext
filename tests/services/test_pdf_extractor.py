from pathlib import Path

from app.services.pdf_service import extract_text_from_pdf


def test_extract_text_from_pdf_returns_expected_content():
    """Verifica que se extrae correctamente el texto de un PDF."""
    # Arrange: Cargar PDF de prueba
    pdf_path = Path(__file__).parent.parent / "fixtures" / "dummy.pdf"
    pdf_bytes = pdf_path.read_bytes()

    # Act: Extraer texto
    extracted_text = extract_text_from_pdf(pdf_bytes)

    # Assert: Verificar contenido esperado
    assert isinstance(extracted_text, str)
    assert len(extracted_text) > 0
    assert "ARCHIVO DE PRUEBA" in extracted_text
    assert "PDF-EXTRACTEXT" in extracted_text
    assert "EXTRACCION EXISTOSA" in extracted_text

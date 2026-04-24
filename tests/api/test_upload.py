from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.pdf_service import extract_text_from_pdf
from app.services.checksum import generate_checksum

client = TestClient(app)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
DUMMY_PDF_PATH = FIXTURES_DIR / "dummy.pdf"


def test_upload_valid_pdf_returns_success():
    """Verifica que al subir un PDF válido retorna éxito con el texto extraído."""
    # Cargar PDF de prueba
    with open(DUMMY_PDF_PATH, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    expected_text = extract_text_from_pdf(pdf_bytes)
    expected_checksum = generate_checksum(pdf_bytes)
    files = {"file": ("dummy.pdf", pdf_bytes, "application/pdf")}

    # Subir archivo
    response = client.post("/upload-pdf", files=files)

    # Verificar respuesta exitosa
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["filename"] == "dummy.pdf"
    assert response_data["extracted_text"] == expected_text
    assert response_data["checksum"] == expected_checksum


def test_upload_txt_file_returns_415():
    """Verifica que al subir un archivo que no es PDF retorna error 415."""
    txt_content = b"Contenido de texto"
    files = {"file": ("test.txt", txt_content, "text/plain")}

    response = client.post("/upload-pdf", files=files)

    assert response.status_code == 415


def test_upload_empty_pdf_returns_400():
    """Verifica que al subir un PDF vacío retorna error 400."""
    empty_content = b""
    files = {"file": ("empty.pdf", empty_content, "application/pdf")}

    response = client.post("/upload-pdf", files=files)

    assert response.status_code == 400

"""
Tests para el endpoint de carga de archivos PDF.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.pdf_service import extract_text_from_pdf


client = TestClient(app)

# Ruta al archivo dummy.pdf
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
DUMMY_PDF_PATH = FIXTURES_DIR / "dummy.pdf"


def test_upload_valid_pdf_returns_success():
    """
    GIVEN a valid PDF file
    WHEN uploaded via POST /upload-pdf
    THEN returns HTTP 200 with filename and real extracted text
    """
    # Given: Load actual PDF file
    with open(DUMMY_PDF_PATH, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    # Get expected extracted text using the real service
    expected_text = extract_text_from_pdf(pdf_bytes)

    files = {"file": ("dummy.pdf", pdf_bytes, "application/pdf")}

    # When
    response = client.post("/upload-pdf", files=files)

    # Then
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["filename"] == "dummy.pdf"
    assert response_data["extracted_text"] == expected_text


def test_upload_txt_file_returns_415():
    """
    GIVEN a non-PDF file (.txt)
    WHEN uploaded via POST /upload-pdf
    THEN returns HTTP 415 (Unsupported Media Type)
    """
    # Given
    txt_content = b"Some text content"
    files = {"file": ("test.txt", txt_content, "text/plain")}

    # When
    response = client.post("/upload-pdf", files=files)

    # Then
    assert response.status_code == 415


def test_upload_empty_pdf_returns_400():
    """
    GIVEN an empty PDF file (0 bytes)
    WHEN uploaded via POST /upload-pdf
    THEN returns HTTP 400 (Bad Request)
    """
    # Given
    empty_content = b""
    files = {"file": ("empty.pdf", empty_content, "application/pdf")}

    # When
    response = client.post("/upload-pdf", files=files)

    # Then
    assert response.status_code == 400

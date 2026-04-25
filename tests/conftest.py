"""Fixtures compartidos para tests."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
DUMMY_PDF_PATH = FIXTURES_DIR / "dummy.pdf"


@pytest.fixture(scope="session")
def pdf_bytes():
    """Bytes del PDF de prueba."""
    return DUMMY_PDF_PATH.read_bytes()


@pytest.fixture(scope="session")
def pdf_text_content():
    """Texto esperado en el PDF de prueba."""
    return {
        "ARCHIVO DE PRUEBA",
        "PDF-EXTRACTEXT",
        "EXTRACCION EXISTOSA",
    }


@pytest.fixture
def sample_text_bytes():
    """Bytes de texto de prueba."""
    return b"contenido de prueba"


@pytest.fixture
def test_client():
    """Cliente de test de FastAPI."""
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)

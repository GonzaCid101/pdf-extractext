"""Fixtures compartidos para tests."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app

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
    return TestClient(app)


@pytest.fixture
async def mongo_client():
    """Cliente MongoDB fresh para cada test."""
    mongo_uri = os.environ.get("MONGO_URI", "")
    client = AsyncIOMotorClient(mongo_uri)
    yield client
    client.close()


@pytest.fixture
async def pdf_collection(mongo_client):
    """Colección de PDFs limpia para cada test."""
    collection = mongo_client.pdf_db.pdfs
    await collection.delete_many({})
    yield collection
    await collection.delete_many({})


@pytest.fixture
async def async_client():
    """Cliente HTTP asíncrono para tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

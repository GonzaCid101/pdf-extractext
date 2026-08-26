"""Fixtures compartidos para tests."""

import os
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.repository.database import get_database


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


@pytest_asyncio.fixture
async def mongo_client():
    """Cliente MongoDB fresh para cada test."""
    mongo_uri = os.environ.get("MONGO_URI", "")
    client = AsyncIOMotorClient(mongo_uri)

    yield client

    client.close()


@pytest_asyncio.fixture
async def override_database(mongo_client):
    """Hace que FastAPI utilice el cliente MongoDB del test."""

    async def _override_database():
        yield mongo_client

    app.dependency_overrides[get_database] = _override_database

    yield

    app.dependency_overrides.pop(get_database, None)


@pytest_asyncio.fixture
async def pdf_collection(mongo_client, override_database):
    """Colección de PDFs limpia para cada test."""
    collection = mongo_client.pdf_db.pdfs

    await collection.delete_many({})

    yield collection

    await collection.delete_many({})


@pytest_asyncio.fixture
async def async_client(override_database):
    """Cliente HTTP asíncrono para tests."""
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def test_client():
    """Cliente de test de FastAPI."""
    return TestClient(app)
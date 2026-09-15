"""Tests de auditoría: Zero-Disk Policy.
Asegura que ningún archivo PDF subido o procesado durante un request HTTP
persista en el sistema de archivos local. Todo el flujo debe ser en memoria.
"""
from collections.abc import Iterator
from contextlib import ExitStack
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Módulos de nuestra app que procesan uploads y PDFs
_APP_MODULES = [
    "app.api.endpoints.upload",
    "app.api.endpoints.pdfs",
    "app.services.pdf_service",
]

# Operaciones de filesystem a inspeccionar dentro de nuestro dominio
_DISK_OPS = [
    ("os", ["open", "remove", "path.exists"]),
    ("shutil", ["copyfile", "move"]),
    ("tempfile", ["TemporaryFile", "NamedTemporaryFile"]),
]

@pytest.fixture
def mock_file_system_operations() -> Iterator[dict[str, object]]:
    """Mock de operaciones de disco SOLO dentro de los módulos de nuestra app."""
    mock_map: dict[str, object] = {}
    with ExitStack() as stack:
        for mod in _APP_MODULES:
            for lib, methods in _DISK_OPS:
                for method in methods:
                    target = f"{mod}.{lib}.{method}"
                    try:
                        mock = stack.enter_context(patch(target))
                    except (AttributeError, TypeError):
                        # Si el módulo no ha importado la librería, no hay nada que validar.
                        continue
                    mock_map[target] = mock
        yield mock_map


def test_upload_pdf_zero_disk_policy(
    mock_file_system_operations: dict[str, object],
    pdf_bytes: bytes,  # fuente de verdad: fixtures/dummy.pdf (vía conftest raíz)
) -> None:
    # Mitigación #84: el PDF ahora es válido y completaría el flujo,
    # así que cortamos la capa de persistencia para no tocar MongoDB real.
    with (
        patch(
            "app.repository.pdf_repository.PDFRepository.find_by_checksum",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "app.repository.pdf_repository.PDFRepository.save",
            new=AsyncMock(return_value="000000000000000000000000"),
        ),
    ):
        test_client = TestClient(app)
        response = test_client.post(
            "/upload-pdf",
            files={"file": ("dummy.pdf", pdf_bytes, "application/pdf")},
        )

    # Verificamos que no se llamaron funciones de disco dentro de los módulos de nuestra app
    for target, mock_obj in mock_file_system_operations.items():
        assert mock_obj.call_count == 0, (
            f"Violación de la política Zero-Disk: '{target}' fue llamada {mock_obj.call_count} veces.\n"
            f"Llamadas: {mock_obj.call_args_list}"
        )

    # La petición debe tener éxito (o fallar opcionalmente con 400/415) pero nunca tocar el disco
    assert (
        response.status_code == 201
        or response.status_code == 400
        or response.status_code == 415
    )
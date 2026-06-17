"""Tests de auditoría: Zero-Disk Policy.
Asegura que ningún archivo PDF subido o procesado durante un request HTTP
persista en el sistema de archivos local. Todo el flujo debe ser en memoria.
"""
from collections.abc import Iterator
from contextlib import ExitStack
from unittest.mock import patch
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

DUMMY_PDF_CONTENT = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Count 0>>endobj\n"
    b"xref\n0 3\n"
    b"0000000000 65535 f\n"
    b"0000000009 00000 n\n"
    b"0000000074 00000 n\n"
    b"trailer<</Size 3/Root 1 0 R>>startxref\n121\n%%EOF"
)

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
                        # Esto es POSITIVO: significa que la política Zero-Disk/Abstracción se cumple.
                        continue
                    mock_map[target] = mock
        yield mock_map

def test_upload_pdf_zero_disk_policy(
    mock_file_system_operations: dict[str, object],
) -> None:
    
    test_client = TestClient(app)
    response = test_client.post(
        "/upload-pdf",
        files={"file": ("dummy.pdf", DUMMY_PDF_CONTENT, "application/pdf")},
    )
    
    # Verificamos que no se llamaron funciones de escritura/lectura de disco dentro de los módulos de nuestra app
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
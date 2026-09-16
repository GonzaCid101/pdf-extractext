"""Tests de auditoria: Verifica que las capas api/ y services/ no tengan conocimiento
ni dependencia directa de la base de datos (motor, pymongo, MongoClient).
"""
import ast
import pytest

FORBIDDEN_DB_NAMES = {"motor", "pymongo", "MongoClient", "AsyncIOMotorClient"}

API_SERVICE_MODULES = [
    ("app.api.endpoints.upload", "app/api/endpoints/upload.py"),
    ("app.api.endpoints.pdfs", "app/api/endpoints/pdfs.py"),
    ("app.services.pdf_service", "app/services/pdf_service.py"),
]
ENDPOINT_MODULES = [
    ("app.api.endpoints.upload", "app/api/endpoints/upload.py"),
    ("app.api.endpoints.pdfs", "app/api/endpoints/pdfs.py"),
]

FORBIDDEN_LAYER_PREFIX = "app.repository"


def _parse_ast(file_path: str) -> ast.AST:
    with open(file_path, "r", encoding="utf-8") as f:
        return ast.parse(f.read(), filename=file_path)


def _get_imported_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                names.add(f"{module}.{alias.name}")
    return names


@pytest.mark.parametrize("module_name, file_path", API_SERVICE_MODULES)
def test_no_forbidden_db_imports(module_name: str, file_path: str) -> None:
    tree = _parse_ast(file_path)
    imports = _get_imported_names(tree)
    found = {
        name for name in imports
        if any(forb in name for forb in FORBIDDEN_DB_NAMES)
    }
    assert not found, (
        f"Abstraccion violada en {module_name}: "
        f"encontrados imports prohibidos {found}. "
        "La lógica de negocio solo debe comunicarse con repository/."
    )


@pytest.mark.parametrize("module_name, file_path", API_SERVICE_MODULES)
def test_no_db_client_usage_in_source(module_name: str, file_path: str) -> None:
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    forbidden_patterns = ["AsyncIOMotorClient", "db.pdf_db", "db[\"", "client.close"]
    found_patterns = [pat for pat in forbidden_patterns if pat in source]
    assert not found_patterns, (
        f"Uso directo de cliente DB detectado en {module_name}: {found_patterns}. "
    )


@pytest.mark.parametrize("module_name, file_path", ENDPOINT_MODULES)
def test_endpoints_do_not_import_repository(module_name: str, file_path: str) -> None:
    tree = _parse_ast(file_path)
    imports = _get_imported_names(tree)
    found = {
        name for name in imports
        if name == FORBIDDEN_LAYER_PREFIX
        or name.startswith(FORBIDDEN_LAYER_PREFIX + ".")
    }
    assert not found, (
        f"Abstraccion violada en {module_name}: "
        f"encontrados imports de la capa repository {found}. "
        "Los endpoints solo deben depender de la capa services/ (puertos)."
    )
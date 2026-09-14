"""Test de auditoría: la capa de servicios depende del port, no del repositorio concreto."""

import ast
from pathlib import Path

FORBIDDEN_CLASS = "PDFRepository"
REPOSITORY_MODULE = "app.repository.pdf_repository"

SERVICES_DIR = Path(__file__).resolve().parents[2] / "app" / "services"


def _imports_forbidden_class(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == REPOSITORY_MODULE:
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module == REPOSITORY_MODULE:
                for alias in node.names:
                    if alias.name == FORBIDDEN_CLASS:
                        return True
    return False


def test_services_do_not_import_concrete_repository() -> None:
    offenders: list[str] = []

    for source_file in SERVICES_DIR.rglob("*.py"):
        tree = ast.parse(
            source_file.read_text(encoding="utf-8"),
            filename=str(source_file),
        )
        if _imports_forbidden_class(tree):
            offenders.append(source_file.name)

    assert not offenders, (
        "La capa de servicios debe depender de PDFRepositoryPort "
        f"(app/services/ports.py), no de la clase PDFRepository. Offenders: {offenders}"
    )

"""Suite consolidada de auditoría arquitectónica."""

import ast
from pathlib import Path

import pytest


APP_ROOT = Path(__file__).resolve().parents[2] / "app"

REPOSITORY_MODULE = "app.repository"
CONCRETE_REPOSITORY_MODULE = f"{REPOSITORY_MODULE}.pdf_repository"
FASTAPI_MODULE = "fastapi"
BSON_MODULE = "bson"



def _parse_ast(file_path: Path) -> ast.AST:
    """Parsea un archivo Python y devuelve su AST."""
    return ast.parse(
        file_path.read_text(encoding="utf-8"),
        filename=str(file_path),
    )


def _get_imported_modules(tree: ast.AST) -> set[str]:
    """Módulos fully-qualified importados en el AST.

    ``import a.b`` -> {"a.b"}
    ``from a.b import c`` -> {"a.b"} (solo el módulo, no el símbolo).
    """
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module)
    return modules


def _py_files(*relative_dirs: str) -> list[Path]:
    """Lista todos los archivos .py de los directorios dados, relativo a APP_ROOT."""
    files: list[Path] = []
    for rel in relative_dirs:
        files.extend(sorted((APP_ROOT / rel).rglob("*.py")))
    return files


def _modules_under(modules: set[str], prefix: str) -> set[str]:
    """Filtra los módulos importados que pertenecen al paquete `prefix`."""
    return {m for m in modules if m == prefix or m.startswith(prefix + ".")}


_REVERSE_DEPENDENCY_CASES = [
    *(
        (
            source_file,
            ("app.api",),
            "services/ no puede depender de la capa API "
            "(la dirección correcta es API -> Services)",
        )
        for source_file in _py_files("services")
    ),
    *(
        (
            source_file,
            ("app.api",),
            "repository/ no puede depender de la capa API "
            "(la dirección correcta es API -> Services <- Repository; "
            "sí está permitido importar app.services para implementar los puertos)",
        )
        for source_file in _py_files("repository")
    ),
]


@pytest.mark.parametrize(
    "source_file, forbidden_prefixes, motive",
    _REVERSE_DEPENDENCY_CASES,
    ids=[str(case[0].relative_to(APP_ROOT)) for case in _REVERSE_DEPENDENCY_CASES],
)
def test_regla_1_direccion_dependencias(
    source_file: Path,
    forbidden_prefixes: tuple[str, ...],
    motive: str,
) -> None:
    imported = _get_imported_modules(_parse_ast(source_file))
    found = {
        module
        for prefix in forbidden_prefixes
        for module in _modules_under(imported, prefix)
    }
    assert not found, (
        f"REGLA 1 violada en {source_file.name}: importa {found}. {motive}."
    )


@pytest.mark.parametrize(
    "source_file",
    _py_files("services"),
    ids=lambda p: p.name,
)
def test_regla_2_services_no_importa_repositorio_concreto(source_file: Path) -> None:
    """services/ debe depender de PDFRepositoryPort, nunca de la clase concreta."""
    imported = _get_imported_modules(_parse_ast(source_file))
    found = _modules_under(imported, CONCRETE_REPOSITORY_MODULE)
    assert not found, (
        f"REGLA 2 violada en {source_file.name}: services importa {found}. "
        f"Debe depender del puerto (PDFRepositoryPort en app/services/ports.py), "
        f"nunca del repositorio concreto '{CONCRETE_REPOSITORY_MODULE}'."
    )



_API_FILES = [
    f for f in _py_files("api") 
    if f.name != "dependencies.py"  # Excluido por ser el Composition Root
]

@pytest.mark.parametrize(
    "source_file",
    _API_FILES,
    ids=lambda p: str(p.relative_to(APP_ROOT)),
)
def test_regla_3_api_no_importa_repository(source_file: Path) -> None:

    """api/ (incluidos endpoints) no debe conocer la capa de persistencia."""
    imported = _get_imported_modules(_parse_ast(source_file))
    found = _modules_under(imported, REPOSITORY_MODULE)
    assert not found, (
        f"REGLA 3 violada en {source_file.name}: la capa API importa {found}. "
        "Los endpoints solo deben depender de services/ (puertos/casos de uso), "
        "nunca de app.repository."
    )


@pytest.mark.parametrize(
    "source_file",
    _py_files("services", "repository"),
    ids=lambda p: str(p.relative_to(APP_ROOT)),
)
def test_regla_4_capas_internas_sin_fastapi(source_file: Path) -> None:
    """Las capas internas deben ser agnósticas del framework web."""
    imported = _get_imported_modules(_parse_ast(source_file))
    found = _modules_under(imported, FASTAPI_MODULE)
    assert not found, (
        f"REGLA 4 violada en {source_file.name}: importa {found}. "
        "services/ y repository/ deben ser agnósticas del framework; "
        "fastapi solo pertenece a la capa api/ (y wiring)."
    )



_NON_REPOSITORY_FILES = _py_files(
    "api", "services", "domain", "models", "core", "exceptions",
)


@pytest.mark.parametrize(
    "source_file",
    _NON_REPOSITORY_FILES,
    ids=lambda p: str(p.relative_to(APP_ROOT)),
)
def test_regla_5_objectid_solo_en_repository(source_file: Path) -> None:
    """bson/ObjectId es un detalle de persistencia limitado a app/repository/."""
    imported = _get_imported_modules(_parse_ast(source_file))
    found = _modules_under(imported, BSON_MODULE)
    assert not found, (
        f"REGLA 5 violada en {source_file.name}: importa {found}. "
        "bson/ObjectId solo puede vivir en app/repository/; "
        "los tipos de la base de datos no deben filtrarse hacia afuera."
    )

# Tests

Esta carpeta contiene los tests unitarios e integrales del proyecto. Los tests de comportamiento verifican la aplicación a través de sus interfaces públicas y siguen la metodología TDD.

## Estructura

- `api/`, `integration/`, `core/`, `domain/`, `exceptions/`, `models/`, `repository/` y `services/`: tests de comportamiento.
- `audits/`: Policy Tests (ver sección siguiente).

## Policy Tests (`tests/audits/`)

Los tests de `tests/audits/` son **Policy Tests**: guardarraíles arquitectónicos y de infraestructura, no tests de comportamiento.

- `test_architecture_policy.py`: inspecciona el AST y los imports para verificar las reglas de dependencia entre capas.
- `test_zero_disk_policy.py`: mockea operaciones de filesystem para verificar que el flujo de upload no escribe en disco.

Estos tests **inspeccionan la implementación** (imports, AST, llamadas a filesystem) y pueden romperse ante un refactor interno aunque el comportamiento externo no cambie. Por eso quedan **fuera del alcance de la regresión funcional**: un fallo allí indica una violación de política arquitectónica, no necesariamente un cambio de comportamiento de la API.

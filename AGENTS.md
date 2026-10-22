# Instrucciones para Agentes de IA

Este proyecto sigue arquitectura en capas con núcleo de dominio y puertos/adaptadores. No se afirma una arquitectura Clean/Hexagonal completa; se documenta lo realmente implementado. Se aplican principios SOLID, KISS, DRY y YAGNI.

## Estructura y convenciones arquitectónicas

### Capas

```
API (app/api/) → Services (app/services/) → Domain (app/domain/)
                        ↑                        ↑
                      Ports                  (núcleo puro)
                        ↓                        ↓
                   Repository (app/repository/) + Mappers
                        ↓
                   Infrastructure (FastAPI/Motor/MongoDB/config)
```

### Dónde vive cada elemento

| Elemento | Ubicación | Notas |
|---|---|---|
| **Dominio (entidad)** | `app/domain/pdf_document.py` | Núcleo puro. Sin dependencias de FastAPI, Pydantic HTTP, Motor o `bson`. |
| **Excepciones de dominio/aplicación** | `app/domain/exceptions.py` | Excepciones puras (`DuplicatePDFError`, `PDFNotFoundError`). Cero acoplamiento con web. Las excepciones HTTP/RFC 9457 viven en `app/exceptions/rfc9457.py`. |
| **Puertos** | `app/services/ports.py` | Contratos (`Protocol`) que definen qué necesita la lógica de aplicación de la persistencia (ej. `PDFRepositoryPort`). Inversión de dependencias. |
| **Casos de uso / lógica de aplicación** | `app/services/` | Dependen de los puertos, nunca de la implementación concreta del repositorio (`app.repository.pdf_repository`). |
| **Mappers** | `app/repository/mappers.py` (MongoDB ↔ Dominio) y `app/api/mappers.py` (Dominio ↔ DTO). | Traducciones explícitas. Los endpoints delegan la construcción de DTOs al mapper de API. |
| **Adaptador de persistencia** | `app/repository/` | Única capa que conoce MongoDB. Aquí viven `pdf_repository.py`, `database.py` y `mappers.py`. |
| **Adaptador HTTP / API** | `app/api/` | Endpoints, `dependencies.py` (Composition Root), `mappers.py`, `upload_reader.py`. |
| **DTOs/esquemas de API** | `app/models/` | Esquemas Pydantic para entrada/salida HTTP. No deben conocer detalles de MongoDB (`_id`/`ObjectId`). |
| **Configuración/infra transversal** | `app/core/` | Configuración (`pydantic-settings`), logging, middleware. |

### Reglas de importación

| Capa | Puede importar FastAPI | Puede importar MongoDB/bson | Restricciones |
|---|---|---|---|
| `app/api/` | Sí | No (salvo a través de excepciones/validación ajena a `bson`) | No debe importar `app.repository`. Usa `app.services` y puertos. `dependencies.py` es el Composition Root. |
| `app/services/` | No | No | Debe depender de `app.services.ports` (no de `app.repository.pdf_repository`). |
| `app/domain/` | No | No | Debe ser puro. |
| `app/repository/` | No | Sí | Única capa autorizada para `bson`/`ObjectId`. Traduce a entidades de dominio. |
| `app/models/` | Parcial (solo tipos usados por FastAPI indirectamente) | No | No debe conocer detalles de persistencia. |
| `app/core/`, `app/exceptions/` | Depende del caso | No | Transversales. |

Estas reglas se verifican con la suite de auditoría arquitectónica en `tests/audits/test_architecture_policy.py`.

## Convención TDD (Test-Driven Development)

Al implementar nuevas funcionalidades, debes evidenciar el ciclo TDD utilizando los siguientes pasos y comentarios explícitos en el código:

1. **RED:** Crea el test unitario primero y verifica que falla. Debe incluir el comentario: `# FASE RED: Este test fallará inicialmente`.
2. **GREEN:** Implementa la solución mínima necesaria para que el test pase. Debe incluir el comentario: `# FASE GREEN: Implementación mínima para pasar el test`.
3. **REFACTOR:** Mejora la implementación manteniendo los tests en verde (aplicando DRY y KISS), sin alterar el comportamiento.
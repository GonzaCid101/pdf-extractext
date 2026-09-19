# Spec — Persistence Service

> Contrato interno del servicio de persistencia. Independiente de implementación.
> Único consumidor: API Service (B1). Único propietario de la base de datos del dominio.
> Trazabilidad: Alignment §4 (fronteras), §6.2 (B2 — unicidad del checksum), §6.4 (R2 — filename largo → 422), §6.5 (ID), §6.7 (idempotencia/409), `common.md`.

## Responsabilidad contractual

Exponer el CRUD de documentos y garantizar los invariantes del dato:

1. **Unicidad del checksum:** jamás existen dos documentos con el mismo checksum. Es una garantía contractual; el mecanismo interno (p. ej. índice único) es detalle de implementación.
2. **Invariantes del dato:** valida lo que persiste (longitud de filename) aunque el consumidor ya lo haya validado.
3. **Generación del ID:** cada documento recibe un identificador al crearse. **Formato v1 CONGELADO:** ObjectId hexadecimal de 24 caracteres (`common.md` §4). Nombre de campo contractual de este servicio: **`id`** (API lo transforma a `_id` en el contrato público).

**No hace (contractual):** no recibe ni procesa el PDF binario (recibe solo JSON), no extrae texto, no inicia llamadas a otros servicios.

## Modelo del documento (vista contractual)

```json
{
  "id": "65797e91c185b4c7c5a93a1b",
  "filename": "documento.pdf",
  "extracted_text": "texto...",
  "checksum": "9f86d081..."
}
```

| Campo | Tipo | En creación | En respuesta | Regla |
|---|---|---|---|---|
| `filename` | string | obligatorio | siempre | longitud máx. 100 (invariante heredada del monolito, `pdf_service.py:26`); violación → 422 (R2) |
| `extracted_text` | string | obligatorio | siempre | puede ser cadena vacía |
| `checksum` | string (64) | obligatorio | siempre | formato según `common.md` §1; sujeto a unicidad |
| `id` | string | — (lo asigna el servicio) | siempre | generado al persistir |

No existe `created_at`/`updated_at` en v1 (pendiente del Alignment; no introducir en el contrato).

---

## POST /documents

- **Request:** `application/json` — `{filename, extracted_text, checksum}`.
- **201:** documento creado completo (incluye `id`).
- **Errores:**
  - 400 — cuerpo faltante o malformado.
  - 422 — filename demasiado largo u otro invariante de datos violado (R2). `code`: `FILENAME_TOO_LONG`.
  - **409 — checksum duplicado.** `code`: `DUPLICATE_CHECKSUM`. **El cuerpo del 409 contiene la representación completa del documento existente** (decisión congelada — `common.md` §4.1). Esto permite a API recuperar el recurso tras un retry cuyo 201 se perdió; no existe endpoint `/exists` ni lookup por checksum.
- **Semántica de repetición (contractual):** la operación no es HTTP-idempotente (1ª vez → 201, reintento → 409), pero tiene efecto acotado: repetirla nunca duplica datos.
- **Errores internos:** 500 (`INTERNAL_ERROR`); 503 si la base de datos es inalcanzable (`DEPENDENCY_UNAVAILABLE`).

**Catálogo de códigos de Persistence (exhaustivo):** `INVALID_REQUEST` (400), `FILENAME_TOO_LONG` (422), `DUPLICATE_CHECKSUM` (409), `NOT_FOUND` (404, en GET/PATCH/DELETE), `INTERNAL_ERROR` (500), `DEPENDENCY_UNAVAILABLE` (503). Formato del envelope: `{code, message}` (`common.md` §3).

## GET /documents

- **200:** lista completa de documentos (array de la vista contractual).
- **Sin paginación** (pendiente del Alignment; no introducir en v1).
- Errores: 500 / 503 ante fallo interno o de base de datos.

## GET /documents/{id}

- **200:** documento completo.
- **400:** `id` con formato inválido (no conforme al formato de ID vigente — `common.md` §4).
- **404:** formato válido, recurso inexistente.
- Errores internos: 500 / 503.

## PATCH /documents/{id}

- **Request:** `{filename}` (único campo actualizable).
- **200:** documento actualizado.
- **Errores:** 400 (id inválido o cuerpo vacío/malformado) · 404 (inexistente) · 422 (filename demasiado largo — R2, la revalidación usa el mismo código que API) · 500/503 internos.
- El `checksum` y `extracted_text` **no** son actualizables contractualmente.
- Actualizar al mismo valor es admisible (efecto idempotente de hecho).

## DELETE /documents/{id}

- **204:** eliminado.
- **Errores:** 400 (id inválido) · 404 (inexistente) · 500/503.
- Un segundo DELETE sobre el mismo id produce 404 (≡ "ya eliminado").

## Health

- **Liveness** y **readiness** (readiness verifica conectividad con la base de datos). Rutas exactas pendientes de la convención de health (Alignment §6.6) — *PENDIENTE hasta su aprobación*.

## Out of scope

Motor/driver concreto, estructura de colecciones, índices como mecanismo, clases internas: Master Plan de Persistence.

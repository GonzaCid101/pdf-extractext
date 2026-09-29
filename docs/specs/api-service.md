# Spec — API Service (contrato público)

> Contrato público del sistema. Independiente de implementación.
> Rol: orquestador (B1) y frontera pública. Traduce los errores internos al contrato público; nunca expone detalles internos.
> Trazabilidad: Alignment §4, §5.2 (flujo), §6.1–6.6, y comportamiento ACTUAL del monolito (`app/api/endpoints/upload.py`, `pdfs.py`).
> Conserva la funcionalidad pública actual; los únicos cambios contractuales deliberados son R2 y R3 (415→422 en los casos indicados).

## Representación pública del documento

```json
{
  "_id": "65797e91c185b4c7c5a93a1b",
  "filename": "documento.pdf",
  "extracted_text": "texto...",
  "checksum": "9f86d081..."
}
```

Conserva los campos del contrato actual del monolito (incluido el nombre `_id` en las respuestas). **Congelado:** el ID v1 es ObjectId hex de 24 caracteres; Persistence usa `id` y **API transforma `id` → `_id`** en el borde público (compatibilidad de clientes y corte Strangler sin fricción), ver `common.md` §4. No se exponen simultáneamente `id` y `_id`. Correlación: `X-Request-ID` presente en respuestas y propagado internamente.

---

## GET /

- **200:** `{"message": "PDF Extractext API funcionando"}` (contrato ACTUAL, sin cambio).

## Health (PROPUESTO en Alignment §6.6 — aún no aprobado)

Liveness (`/health`) y readiness (`/health/ready`, verifica Extraction y Persistence; 503 si alguna falla) figuran como PROPUESTAS del Alignment. **No forman parte de este contrato hasta su aprobación.**

## POST /upload-pdf

Orquestación: valida entrada → envía el PDF a Extraction → envía el resultado a Persistence → responde. (Detalle de orquestación: Alignación §5.2; no forma parte del contrato visible del cliente salvo en errores de dependencia.)

### Request

- **Content-Type:** `multipart/form-data`
- **Campo:** `file` — el PDF.

### Response 201

Representación pública del documento (ver arriba).

### Retry interno ante respuesta perdida — CONGELADO

Escenario: API hace `POST /documents`; Persistence crea el documento pero la respuesta 201 se pierde (timeout/red); API reintenta; Persistence responde **409 + `DUPLICATE_CHECKSUM` + documento existente completo** (`persistence-service.md`).

Comportamiento contractual de API:

1. Si API recibe 409 con el documento existente y puede determinar que corresponde al archivo del upload en curso, **responde al cliente `201` con la representación pública del documento** — la creación ocurrió; el conflicto interno **no se expone** al cliente.
2. El mapeo se realiza mediante `status + code`, nunca parseando `message` (D8).

### Errores

| Caso | Código | Origen |
|---|---|---|
| Archivo vacío | 400 | API (ACTUAL) |
| Tamaño supera el máximo (50 MB hoy) | 413 | API (ACTUAL) |
| Extensión / media type no soportado | **415** | API (ACTUAL; 415 queda reservado exclusivamente a este caso — R2/R3) |
| Filename demasiado largo | **422** | API (R2 — en el monolito hoy es 415; cambio contractual confirmado) |
| Contenido no procesable como PDF | **422** | traducido desde Extraction (R3 — en el monolito hoy es 415; cambio contractual confirmado) |
| Documento duplicado (mismo checksum) | **409** | traducido desde Persistence (ACTUAL, formato RFC 9457) — **excepción:** ver "Retry interno" abajo |
| Body multipart malformado / campo faltante | 400 / 422 | validación estructural (422 es el comportamiento por defecto actual del framework) |
| Extraction o Persistence inalcanzable | 503 | API (PROPUESTO D9) |
| Timeout hacia una dependencia | 504 | API (PROPUESTO D9) |
| Fallo interno inesperado | 500 | API |

## GET /pdfs

- **200:** lista completa de documentos (representación pública).
- **Sin paginación** (pendiente del Alignment; no introducir en v1).
- Errores: 503 si Persistence es inalcanzable (PROPUESTO D9).

## GET /pdfs/{id}

- **200:** documento.
- **400:** `id` con formato inválido (ACTUAL; el contrato conserva el comportulario actual — formato según `common.md` §4).
- **404:** inexistente.
- Errores de dependencia: 503 (PROPUESTO D9).

## PATCH /pdfs/{id}

- **Request:** `{"filename": "..."}`; campos desconocidos rechazados (ACTUAL: `extra="forbid"` → 422).
- **200:** documento actualizado.
- **400:** body vacío o id inválido (ACTUAL).
- **404:** inexistente.
- **422:** filename demasiado largo (R2) o campos no permitidos (ACTUAL).
- Errores de dependencia: 503 (PROPUESTO D9).

## DELETE /pdfs/{id}

- **204:** eliminado (ACTUAL).
- **400:** id inválido (ACTUAL). **404:** inexistente. **503:** dependencia (PROPUESTO D9).

---

## Errores: público vs interno

- El cliente solo recibe los códigos listados arriba con el formato público (RFC 9457 — **PENDIENTE** de aprobación, Alignment §6.6; hoy el monolito mezcla RFC 9457 con `{"detail"}`).
- Los errores que API recibe de Extraction y Persistence usan el envelope interno congelado `{code, message}` (D8 — `common.md` §3). API traduce mediante `status + code`. Códigos internos referenciados por este contrato: de Extraction `INVALID_REQUEST`, `INVALID_PDF_CONTENT`, `INTERNAL_ERROR`; de Persistence `INVALID_REQUEST`, `FILENAME_TOO_LONG`, `DUPLICATE_CHECKSUM`, `NOT_FOUND`, `INTERNAL_ERROR`, `DEPENDENCY_UNAVAILABLE`. Los catálogos completos y su ownership están en la Spec de cada servicio.

## Dependencias de otros contratos

- Hacia Extraction: `POST /extract` (ver `extraction-service.md`).
- Hacia Persistence: CRUD `/documents` (ver `persistence-service.md`).
- Timeouts, retries y backoff: fuera del contrato → Master Plan de API (principio: centralizados en API, solo errores de transporte).

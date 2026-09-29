# Spec — Extraction Service

> Contrato interno del servicio de extracción. Independiente de implementación.
> Trazabilidad: Alignment §4 (fronteras), §6.1 (B1 — no llama a nadie), §6.2 (B2 — calcula el checksum), §6.3 (B3 — entrada multipart), §6.6 (R3 — clasificación de errores), `common.md`.

## Responsabilidad contractual

Recibir un PDF, extraer su texto, calcular su checksum y devolver ambos. Es stateless: ningún resultado sobrevive a la respuesta.

**No hace (contractual):** no persiste, no accede a bases de datos, no llama a otros servicios, no valida reglas de negocio del dominio (p. ej. límite de longitud de filename: esa regla pertenece a API y Persistence), no se expone a internet.

---

## POST /extract

Único endpoint de negocio del servicio.

### Request

- **Método / Content-Type:** `POST` · `multipart/form-data`
- **Campo:** `file` — el PDF completo (bytes)
- El filename viaja como el nombre del archivo en la parte multipart (mismo mecanismo que el contrato público de upload).
- No hay otros campos contractuales.

### Response 200

```json
{
  "filename": "documento.pdf",
  "extracted_text": "texto extraído...",
  "checksum": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
}
```

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `filename` | string | sí | el filename recibido, sin modificar |
| `extracted_text` | string | sí | texto completo extraído; puede ser cadena vacía si el PDF no contiene texto extraíble (no es un error en sí mismo) |
| `checksum` | string (64) | sí | SHA-256 de los bytes recibidos, según `common.md` §1 |

Garantías del proveedor:

- Si responde 200, los tres campos están presentes y el checksum corresponde exactamente a los bytes recibidos.
- No hubo efectos laterales (nada persistido, nada encolado).

### Errores

Formato: envelope interno congelado `{code, message}` (`common.md` §3). API traduce mediante `status + code`.

| Caso | HTTP | `code` | Clase |
|---|---|---|---|
| Campo `file` ausente o payload multipart malformado | 400 | `INVALID_REQUEST` | input |
| El contenido no puede procesarse como PDF (corrupto, no-PDF con nombre .pdf) | **422** | `INVALID_PDF_CONTENT` | input (R3) |
| Fallo interno durante el procesamiento (recurso agotado, error inesperado) | 500 | `INTERNAL_ERROR` | interno |

**Catálogo de códigos de Extraction (exhaustivo):** `INVALID_REQUEST`, `INVALID_PDF_CONTENT`, `INTERNAL_ERROR`.

Regla R3 (contractual): la respuesta de error debe permitir a API distinguir, sin reinterpretar, entre "culpa del input" (4xx) y "fallo interno" (5xx). El servicio clasifica internamente antes de responder; **nunca** se confunde PDF corrupto con fallo interno.

Códigos **no usados** por este contrato: 415 (no valida media type — esa regla es del borde público), 409 (no persiste, no detecta duplicados), 404 (sin recursos).

## Health

- **Liveness** requerida: proceso vivo, **sin** verificar dependencias (no tiene). Ruta exacta: convención pendiente de aprobación (Alignment §6.6, PROPUESTO `GET /health`); hasta su congelación, *PENDIENTE*.

## Out of scope

- Elección de librería de extracción, clases internas, manejo de memoria: Master Plan de Extraction.

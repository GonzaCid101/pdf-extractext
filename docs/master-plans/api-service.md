# Master Plan — API Service

> **Estado:** base de trabajo para crear Issues/Subissues. No es una Issue ni un plan de implementación detallado por tareas; define el *qué* y el *orden lógico*. El *cómo* (librerías, estructura interna, Docker) se decide al ejecutar, respetando AGENTS.md (Clean Architecture, TDD).
>
> **Fuentes de verdad (no reinterpretar):**
> - `docs/architecture/microservices-alignment-analysis.md` (decisiones CONFIRMADAS: B1, B2, B3, R2, R3; D8/ID/409 congelados en Specs)
> - `docs/specs/common.md`, `docs/specs/api-service.md`, `docs/specs/extraction-service.md`, `docs/specs/persistence-service.md`
> - `api-service-analysis.md` (análisis individual previo)
> - Monolito actual (`app/`) solo como referencia del comportamiento público a preservar.

---

## 1. Propósito y alcance

El API Service es la **única frontera pública** del sistema y el **orquestador** del flujo de upload. Su responsabilidad: exponer el contrato público (upload + CRUD), validar la entrada en el borde, llamar a Extraction y Persistence, traducir sus respuestas y errores al contrato público, y transformar las representaciones de datos entre ambos planos.

**Fuera de su responsabilidad (CONFIRMADO, no negociable):**
- No extrae texto (eso es Extraction).
- No calcula checksums (B2 — los transporta).
- No accede a MongoDB ni a Dragonfly (Persistence es el único dueño de Mongo; Dragonfly está fuera de v1).
- No persiste nada.
- No recibe ni procesa reglas de negocio del dominio más allá de la validación de entrada del contrato público.

---

## 2. Fuentes y dependencias

**Fuentes de este plan:** las listadas en el encabezado. En caso de conflicto, el orden de autoridad es: Alignment → Specs → análisis individual → monolito.

**Dependencias de este servicio:**

| Dependencia | Contrato | Dirección | Uso |
|---|---|---|---|
| Extraction Service | `docs/specs/extraction-service.md` (C1) | API → Extraction, `POST /extract`, multipart | Solo durante el upload |
| Persistence Service | `docs/specs/persistence-service.md` (C2) | API → Persistence, JSON, CRUD `/documents` | Upload y todo el CRUD público |
| Infrastructure | Alignment §9 | API es consumida vía Traefik; recibe URLs de dependencias por configuración | Deployment, redes, health |

API **no tiene otras dependencias de servicio**. Extraction y Persistence no se conocen entre sí (B1); cualquier comunicación cruzada pasa por API.

---

## 3. Responsabilidades

1. **Exponer el contrato público completo** (`docs/specs/api-service.md`): upload, CRUD de PDFs y `GET /`.
2. **Orquestar el upload:** entrada → Extraction → Persistence → respuesta.
3. **Validación de entrada en el borde (fail-fast):** extensión/media type, tamaño, archivo vacío, longitud del filename, formato de ID recibido.
4. **Cliente de Extraction:** enviar el PDF por `multipart/form-data` y recibir `{filename, extracted_text, checksum}`.
5. **Cliente de Persistence:** operar el CRUD JSON de `/documents`.
6. **Transformación de modelos:** `id` (Persistence) → `_id` (público), nunca ambos.
7. **Traducción de errores:** de envelope interno `{code, message}` + status → contrato público, sin exponer detalles internos.
8. **Retry ante respuesta perdida** (`POST /documents`): resolución del 409 con documento existente → 201 al cliente (§8).
9. **Preservar la funcionalidad pública actual** del monolito, con los únicos cambios contractuales aprobados: 422 para filename largo (R2) y para PDF no procesable (R3).
10. **Observabilidad mínima:** propagar `X-Request-ID` en toda la cadena; logging coherente con la práctica actual del monolito.

---

## 4. Contratos que debe implementar

Resumen de `docs/specs/api-service.md` (la Spec manda; esto es guía):

| Endpoint | Puntos contractuales clave |
|---|---|
| `GET /` | 200 con mensaje de estado (sin cambio respecto del monolito) |
| `POST /upload-pdf` | multipart `file` → 201 con documento público. Errores: 400 vacío, 413 tamaño, 415 extensión/media type, 422 filename largo (R2), 422 PDF no procesable (R3), 409 duplicado |
| `GET /pdfs` | 200 lista completa; sin paginación en v1 |
| `GET /pdfs/{id}` | 200; 400 ID inválido; 404 inexistente |
| `PATCH /pdfs/{id}` | body `{filename}` únicamente; 200; 400 vacío/ID inválido; 404; 422 filename largo o campos no permitidos |
| `DELETE /pdfs/{id}` | 204; 400 ID inválido; 404 |

En todos los endpoints, ante dependencia inalcanzable: 503; ante timeout de dependencia: 504 (ambos **PROPUESTOS D9**, ver §13). El formato del cuerpo de error público (RFC 9457) es pendiente (§13); las tablas de códigos de la Spec son obligatorias desde ya.

---

## 5. Contratos que debe consumir

### De Extraction (`POST /extract`)
- Enviar: multipart, campo `file` (bytes + filename).
- Recibir 200: `{filename, extracted_text, checksum}` (checksum = SHA-256 hex lowercase 64 chars — definición única en `common.md`).
- Errores posibles: 400 `INVALID_REQUEST`, 422 `INVALID_PDF_CONTENT`, 500 `INTERNAL_ERROR`. API **traduce por status + code, nunca por el texto del message**.

### De Persistence (CRUD `/documents`)
- `POST /documents` con `{filename, extracted_text, checksum}` → 201 documento (`id`) o 409 `DUPLICATE_CHECKSUM` **con el documento existente en el cuerpo**.
- `GET /documents`, `GET /{id}`, `PATCH /{id}` (`{filename}`), `DELETE /{id}` con sus códigos (400/404/422/…).
- Errores internos de Persistence: 500 `INTERNAL_ERROR`, 503 `DEPENDENCY_UNAVAILABLE`.
- Toda respuesta de error interna usa el envelope `{code, message}` congelado (`common.md` §3).

---

## 6. Flujo principal de upload

```text
Cliente
  │  POST /upload-pdf (multipart)
  ▼
API SERVICE
  │  valida entrada (extensión, tamaño, vacío, filename)
  │  POST /extract  ──multipart──▶  EXTRACTION
  │                                   (extrae texto + calcula checksum)
  │  ◀──── {filename, extracted_text, checksum}
  │
  │  POST /documents ────JSON──▶  PERSISTENCE
  │                                (garantiza unicidad de checksum)
  │  ◀──── 201 documento (id)  |  409 + documento existente
  ▼
Cliente ◀── 201 documento público (campo `_id`)
```

Decisiones congeladas que rigen el flujo:
- Extraction calcula el checksum; **API no lo calcula** (B2).
- Persistence garantiza unicidad; el 409 duplicado es un resultado normal (B2).
- Extraction **no** llama a Persistence; **API es el orquestador** (B1).
- Bytes del PDF solo viven en memoria durante la request (stateless en ambos extremos).

---

## 7. Manejo y transformación de errores

Regla central: **status = clase, code = causa** (`common.md` §3). API mapea (`status`, `code`) → respuesta pública; jamás parsea `message`.

| Origen | Entrada interna | Salida pública |
|---|---|---|
| Extraction 422 `INVALID_PDF_CONTENT` | input inválido | 422 (R3) |
| Extraction 400 `INVALID_REQUEST` | input inválido | 400 |
| Extraction 500 `INTERNAL_ERROR` o caída | interno | 503/504 según corresponda (pendiente D9); nunca 500 con detalle interno |
| Persistence 409 `DUPLICATE_CHECKSUM` | conflicto | 409 público **o** resolución de retry (§8) |
| Persistence 422 `FILENAME_TOO_LONG` | input inválido | 422 (R2) |
| Persistence 400/404 | según endpoint | 400/404 público |
| Persistence 503 `DEPENDENCY_UNAVAILABLE` | interno | 503 |
| Entrada del cliente inválida en API | validación propia | 400/413/415/422 según tabla de la Spec |

No se inventan códigos nuevos. Todo código no listado en las Specs es un defecto de implementación.

---

## 8. Retry ante respuesta perdida (decisión congelada)

Escenario cubierto: `POST /documents` → Persistence inserta → la respuesta 201 se pierde → API no sabe si se creó.

Comportamiento contractual de API:
1. API **puede reintentar** `POST /documents` ante fallo de transporte (los valores concretos de cantidad/timeout/backoff pertenecen a la implementación — fuera de este documento).
2. Si el retry responde `409 DUPLICATE_CHECKSUM` **y el cuerpo contiene el documento existente**, API determina que la operación original se completó.
3. En ese caso API responde al cliente **201** con la representación pública del documento existente (la creación de hecho ocurrió).
4. **Un 409 nunca se convierte en 201 por defecto:** solo cuando el documento devuelto corresponde al upload en curso. Un 409 recibido directamente de un checksum ya persistido con anterioridad se traduce como **409 público**, como hoy.
5. El 409 interno no se expone al cliente cuando API pudo resolver la operación.

---

## 9. Transformaciones de datos

- **Identificación:** `Persistence.id` → **público `_id`** (transformación en API). No se exponen nunca ambos. Sin lógica adicional: renombrado de campo al serializar.
- **Documento público:** `_id`, `filename`, `extracted_text`, `checksum` (mismos campos que el contrato actual del monolito).
- **Upload:** el `filename` y los bytes entran por multipart y se reenvían a Extraction sin alteración; la respuesta de Extraction alimenta `POST /documents` sin re-procesamiento.
- **PATCH público:** acepta `{filename}`; valida y reenvía a Persistence. Campos desconocidos → 422 (comportamiento actual con `extra="forbid"`).
- **Correlación:** propagar `X-Request-ID` recibido; si no viene, generarlo (como hace el middleware actual del monolito).

---

## 10. Capacidades a desarrollar

Enumeración funcional (cada una será Issue/Subissue posterior; sin asignar personas):

1. **Base del servicio:** skeleton del servicio, configuración (URLs de Extraction y Persistence, límites de tamaño), health inicial.
2. **Endpoints públicos de lectura:** `GET /`, `GET /pdfs`, `GET /pdfs/{id}`.
3. **Endpoints públicos de escritura:** `PATCH`, `DELETE /pdfs/{id}`.
4. **Cliente HTTP hacia Persistence** (CRUD, envelope de error, código de catálogo).
5. **Cliente HTTP hacia Extraction** (multipart, envelope de error).
6. **Orquestación del upload** (endpoint `POST /upload-pdf` validaciones + cadena Extraction → Persistence).
7. **Transformación de modelos** (`id`→`_id`, mapeo de documento público).
8. **Traducción de errores** (tabla `status+code` → público, envelope interno, formato público).
9. **Retry y resolución de 409** (§8).
10. **Validaciones de borde** (extensión, tamaño, vacío, filename, formato de ID, campos del PATCH).
11. **Observabilidad:** propagación de `X-Request-ID` y logging.
12. **Testing:** unitario, contract tests como consumidor (C1, C2) y como proveedor (C3), integración.

---

## 11. Orden lógico de implementación

Dependencias entre capacidades (no es cronograma):

```text
1 (base/config) ──▶ 4 (cliente Persistence) ──▶ 2 y 3 (CRUD público)
                ╲─▶ 5 (cliente Extraction) ──▶ 6 (orquestación upload)
7 (transformaciones) y 8 (traducción errores) acompañan a cada capacidad que las necesita
9 (retry/409) depende de 4 y 6
10 valida junto a cada endpoint (fail-fast temprano)
11 observabilidad transversal, temprana pero incremental
12 testing acompaña cada capacidad (TDD); contract tests C3 desde el inicio
```

- Se puede empezar por CRUD público (solo necesita Persistence) en paralelo al cliente de Extraction.
- El upload es la última pieza funcional (necesita ambos clientes).
- Health/readiness depende de la decisión pendiente (§13); implementar liveness simple primero.

---

## 12. Integración con los otros servicios

### Con Extraction
- API consume C1 tal cual; no le exige validaciones de negocio (la extensión ya se valida en API; el filename largo es regla de dominio validada por API/Persistence).
- Debe tolerar y traducir su catálogo completo: `INVALID_REQUEST`, `INVALID_PDF_CONTENT`, `INTERNAL_ERROR`.

### Con Persistence
- API consume C2 tal cual, incluida la semántica del 409 con documento.
- Nunca escribe en Mongo directamente; todas las lecturas pasan por Persistence.
- Debe tolerar su catálogo completo de códigos.

### Con Infrastructure
- API declara necesidades: puerto propio (convención pendiente en Master Plan de Infra), variables para URLs de dependencias, health endpoints para orquestación de arranque (`depends_on` + readiness cuando se apruebe).
- No conoce Traefik; solo responde al contrato público.

**Frontera dura:** qualquier necesidad de datos no cubierta por C2 es una discusión de Spec, no un acceso directo.

---

## 13. Decisiones pendientes que afectan al API Service

Solo se listan; no se resuelven aquí.

1. **Formato del cuerpo de error público (RFC 9457)** — PROPUESTO (Alignment §6.6). Hasta su aprobación, mantener el formato actual del monolito como referencia y dejar el punto aislado (cambiar formato ≠ cambiar códigos).
2. **503/504 ante dependencias** — PROPUESTO (D9). Si no se aprueba, el comportamiento actual sería 500 genérico; las tablas de errores deben quedar listas para ambos.
3. **Health endpoints públicos (`/health`, `/health/ready`)** — PROPUESTO. No exponer hasta aprobación.
4. **Valores de retry/timeout/backoff** — se definen en implementación, guiados por principio (centralizados en API, solo transporte).
5. **Paginación de `GET /pdfs`** — fuera de v1.

---

## 14. Criterios de finalización del Master Plan

Este Master Plan se considera suficiente para derivar Issues/Subissues cuando:

- [ ] Toda capacidad de §10 tiene trazabilidad a una sección de Spec (C3 propio, C1/C2 consumidos).
- [ ] Las decisiones CONFIRMADAS/congeladas (B1, B2, B3, R2, R3, D8, ID, 409) están reflejadas sin reinterpretación.
- [ ] Las decisiones pendientes (§13) no bloquean ninguna capacidad salvo health público (queda postergado).
- [ ] El orden lógico (§11) permite empezar por una capacidad pequeña y testeable sin esperar a las demás.
- [ ] Cada Issue futura podrá escribirse con: alcance (capacidad), contrato afectado (Spec+sección), errores a traducir (catálogo), criterio de aceptación verificable contra contract tests.
- [ ] Nada de este documento contradice Alignment ni Specs.

**No incluye (a propósito):** librerías HTTP, estructura de carpetas, Dockerfile, valores de timeout, asignación de personas, ni Issues. Eso viene después.

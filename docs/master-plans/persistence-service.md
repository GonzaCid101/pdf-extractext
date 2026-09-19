# Master Plan — Persistence Service

> **Estado:** base de trabajo para crear Issues/Subissues. No es un plan de implementación detallado ni define tareas concretas.
>
> **Fuentes de verdad (no reinterpretar):**
> - `docs/architecture/microservices-alignment-analysis.md` (B1, B2, R2; ownership §7; errores §6.6)
> - `docs/specs/persistence-service.md` (contrato C2 que este servicio provee)
> - `docs/specs/common.md` (checksum, HTTP status, envelope `{code, message}`, IDs, semántica del 409)
> - `docs/specs/api-service.md` y `docs/specs/extraction-service.md` (solo contexto del consumidor y del productor)
> - `persistence-analysis.md` (análisis individual previo)
> - Monolito actual (`app/repository/`, `app/services/pdf_service.py`) solo como referencia del comportamiento a migrar.

---

## 1. Propósito y alcance

El Persistence Service es el **único dueño de los datos** del dominio y el **único servicio que habla con MongoDB**. Expone un CRUD interno de documentos con garantías de integridad (unicidad de checksum, invariantes del dato) hacia su único consumidor: API Service.

**Fuera de alcance (contractual, no negociable):**
- Extracción de PDF y cálculo de checksum (eso llega ya hecho).
- Orquestación de flujos (es de API).
- Contrato público / clientes externos (frontera de API).
- Llamadas a Extraction o a cualquier otro servicio.
- Responsabilidades de plataforma (redes, Traefik, volúmenes): Infrastructure.

## 2. Fuentes y dependencias

**Grafo de dependencias:**

```text
API → Persistence → MongoDB

Persistence ↛ Extraction
Extraction  ↛ Persistence
Extraction  ↛ MongoDB
API         ↛ MongoDB
```

| Relación | Dirección | Naturaleza |
|---|---|---|
| API Service | API → Persistence | Único consumidor. JSON (B3) |
| Extraction | — | **No existe relación.** Persistence jamás lo llama ni lo conoce |
| MongoDB | Persistence → MongoDB | Único servicio con acceso; ownership exclusivo |
| Infrastructure | Infra aloja Persistence y MongoDB | Red interna, healthchecks, volúmenes (detalles: Master Plan de Infrastructure) |

## 3. Responsabilidades

1. Exponer el CRUD interno de documentos (`/documents`).
2. Recibir documentos ya procesados: `{filename, extracted_text, checksum}`.
3. Persistirlos en MongoDB y devolverlos con `id`.
4. **Generar/gestionar el `id`** del documento (formato congelado: ObjectId hex de 24 caracteres).
5. **Garantizar la unicidad del checksum** como invariante de base de datos (mecanismo = detalle de implementación).
6. **Validar invariantes contractuales** antes de persistir (p. ej. longitud de filename → 422, R2), aunque API ya valide en el borde.
7. Clasificar errores mediante status + `code` estable.
8. Manejar el conflicto de unicidad según la decisión congelada (409 + documento existente, §7).
9. Exponer health (liveness y, cuando se apruebe la convención, readiness con verificación de Mongo).

## 4. Contrato que debe implementar

Resumen de `docs/specs/persistence-service.md` (la Spec manda):

| Endpoint | Entrada | Salida OK | Errores relevantes |
|---|---|---|---|
| `POST /documents` | JSON `{filename, extracted_text, checksum}` | 201 documento con `id` | 400 · 409 `DUPLICATE_CHECKSUM` (+documento) · 422 `FILENAME_TOO_LONG` |
| `GET /documents` | — | 200 lista completa (sin paginación en v1) | 500/503 |
| `GET /documents/{id}` | path `id` | 200 documento | 400 formato inválido · 404 · 500/503 |
| `PATCH /documents/{id}` | JSON `{filename}` | 200 documento actualizado | 400 · 404 · 422 · 500/503 |
| `DELETE /documents/{id}` | path `id` | 204 | 400 · 404 · 500/503 |

Reglas: JSON only (nunca binarios); `checksum` y `extracted_text` no son actualizables; DELETE repetido → 404 ("ya eliminado"); todos los errores usan el envelope `{code, message}`.

## 5. Modelo de datos y ownership

Documento persistido (vista contractual):

```json
{
  "id": "65797e91c185b4c7c5a93a1b",
  "filename": "documento.pdf",
  "extracted_text": "texto...",
  "checksum": "9f86d081..."
}
```

| Campo | Regla |
|---|---|
| `id` | Generado y gestionado por Persistence (v1: ObjectId hex 24). Identificador contractual interno |
| `filename` | Invariante: longitud ≤ 100; violación → 422 |
| `extracted_text` | string, puede ser vacío |
| `checksum` | SHA-256 hex lowercase 64 (`common.md` §1); **único** en toda la colección |

Reglas de frontera de identificación:
- **Persistence usa `id`; nunca expone `_id`** como campo contractual.
- **API transforma `id` → `_id`** para el público. `id` y `_id` no coexisten en el contrato interno.
- `created_at` / `updated_at`: **no se introducen en v1** (pendientes del Alignment, no bloqueantes).

## 6. Persistencia y MongoDB

Responsabilidades sobre MongoDB (sin decisiones de implementación — clases, repositorios, drivers y nombres de archivo quedan para los Issues/implementación):

- Conexión y ciclo de vida del cliente de base de datos.
- Operaciones: insertar, consultar por id, listar, actualizar parcial, eliminar.
- Garantía de unicidad del checksum a nivel de base (el mecanismo es interno; la garantía es contractual).
- Traducción de errores de persistencia (duplicado de clave, base inalcanzable) al catálogo contractual de la Spec.
- Gestión del arranque con la garantía de unicidad disponible (el Alignment advierte: durante la convivencia con el monolito debe existir un solo dueño de índices/esquema — riesgo del Strangler, coordinar con Infrastructure).

**Ningún otro servicio accede a MongoDB.** Ni API, ni Extraction, ni el monolito después del corte.

## 7. Unicidad y `409 DUPLICATE_CHECKSUM`

Decisión congelada (Alignment §6.7 / `common.md` §4.1 / `persistence-service.md`):

- Persistence garantiza la unicidad del checksum.
- Una duplicación produce **409** con `code: DUPLICATE_CHECKSUM`.
- **El cuerpo del 409 contiene el documento existente completo** (contrato interno: con `id`).
- No existe endpoint `/exists` ni lookup por checksum.
- No existe `Idempotency-Key` ni almacenamiento de idempotencia en v1.

Distinción semántica (Persistence solo informa; la decisión final es de API):

```text
409 "normal"
  → conflicto real: el documento ya existía antes del upload
  → API lo expone como 409 público

409 tras respuesta 201 perdida + retry
  → Persistence informa que el documento ya existe (mismo contenido)
  → API determina que la creación ocurrió y responde 201 al cliente
```

**Persistence no decide cuándo API responde 201.** Su única obligación contractual es informar el conflicto correctamente y devolver el documento existente. Toda la lógica de retry y de resolución vive en API.

## 8. Manejo de errores

Catálogo contractual exhaustivo (de `persistence-service.md`):

| HTTP | code | Significado |
|---|---|---|
| 400 | `INVALID_REQUEST` | cuerpo faltante/malformado, id con formato inválido |
| 404 | `NOT_FOUND` | recurso inexistente |
| 409 | `DUPLICATE_CHECKSUM` | unicidad violada; cuerpo incluye documento existente |
| 422 | `FILENAME_TOO_LONG` | invariante de dato violado (R2) |
| 500 | `INTERNAL_ERROR` | fallo interno no clasificado |
| 503 | `DEPENDENCY_UNAVAILABLE` | MongoDB inalcanzable |

Reglas:
- Envelope interno **siempre** `{code, message}` (congelado).
- `code` es estable y obligatorio; `message` es diagnóstico.
- El consumidor (API) decide por `status + code`; nunca parsea `message`.
- No se inventan códigos adicionales: este catálogo es cerrado en v1.

## 9. Capacidades a desarrollar

Enumeración funcional (luego se convierten en Issues; sin asignación):

1. **Base del servicio:** skeleton y configuración mínima de ejecución.
2. **Conexión y ownership de MongoDB:** ciclo de vida del cliente y acceso exclusivo.
3. **Modelo contractual de documentos:** representación interna alineada a la Spec (`id`, `filename`, `extracted_text`, `checksum`).
4. **Unicidad de checksum:** garantía de base + traducción de conflicto a `409 DUPLICATE_CHECKSUM` con documento existente.
5. **Creación:** `POST /documents` con generación de `id`.
6. **Lecturas:** `GET /documents` (lista completa) y `GET /documents/{id}`.
7. **Actualización:** `PATCH /documents/{id}` solo `filename`, con revalidación del invariante (422).
8. **Eliminación:** `DELETE /documents/{id}`.
9. **Validación de invariantes:** longitud de filename como regla del dueño del dato.
10. **Manejo de errores:** envelope `{code, message}` + catálogo cerrado.
11. **Testing:** unitario, contract tests como proveedor de C2 (incl. 409 con documento), integración contra Mongo real (preserva la práctica del monolito).
12. **Integración con API:** verificación del CRUD y del flujo upload completo.

## 10. Orden lógico de implementación

Dependencias lógicas (no cronograma):

```text
1 base/config ──▶ 2 conexión MongoDB ──▶ 3 modelo contractual
                                          ↓
                          4 unicidad ──▶ 5 creación (POST)
                                          ↓
                          6 lecturas ──▶ 7 actualización ──▶ 8 eliminación
                                          ↓
                          9 validación de invariantes (acompaña 5 y 7)
                                          ↓
                          10 manejo de errores (transversal)
                                          ↓
                          11 testing por capacidad (TDD)
                                          ↓
                          12 integración con API
```

- 4 (unicidad) debe existir **antes** de 5: `POST /documents` sin garantía de unicidad viola el contrato.
- 9 y 10 se construyen junto a las operaciones que los usan, no al final.
- Testing sigue TDD: cada capacidad nace con sus tests (incluidos contract tests C2).

## 11. Integración con los otros servicios

```text
API → Persistence
Persistence → MongoDB

Extraction ↛ Persistence
Persistence ↛ Extraction
API ↛ MongoDB
Extraction ↛ MongoDB
```

| Servicio | Condición de integración |
|---|---|
| **API** | Único consumidor. La entrada de creación es directamente compatible con la salida de Extraction (`{filename, extracted_text, checksum}` — mismos nombres de campo). Persistence responde con `id` interno; API transforma a `_id`. Debe tolerar el catálogo completo de códigos |
| **Extraction** | Ninguna relación. No importar nada suyo, no conocer su contrato |
| **Infrastructure** | Mongo accesible solo desde la red de Persistence; readiness futuro dependerá de la conectividad con Mongo; volumen de datos gestionado por Infra (hoy `infra/mongodata/` contiene datos versionados — riesgo documentado en Alignment §9) |

## 12. Fronteras y ownership

### Persistence posee
- Documentos persistidos y su integridad.
- MongoDB (exclusivo).
- Generación/gestión de `id`.
- Unicidad del checksum.
- Invariantes de persistencia (p. ej. longitud de filename).
- CRUD interno.

### Persistence no posee
- Extracción de texto ni cálculo de checksum (llega calculado).
- Orquestación ni flujo de upload.
- Contrato público ni decisión sobre qué responde el cliente final.
- Retries (son de API).
- Traefik, redes, clientes finales.

Ninguna capacidad del plan asigna responsabilidades cruzadas.

## 13. Decisiones pendientes (que afectan a Persistence)

Solo se listan; no se resuelven aquí.

1. **Health liveness/readiness:** convención PROPUESTA (Alignment §6.6). El readiness de Persistence verificaría Mongo, pero rutas y profundidad exactas quedan pendientes de aprobación.
2. **RFC 9457 en borde público:** afecta solo a API; Persistence usa siempre el envelope interno `{code, message}` (ya congelado).
3. **Paginación de `GET /documents`:** fuera de v1 (no introducir).
4. **`created_at` / `updated_at`:** no existen hoy; no introducir.
5. **Detalles de plataforma** (puertos, versión de Mongo, volúmenes, topología de red): Master Plan de Infrastructure.

No hay decisiones nuevas; no hay pendientes bloqueantes.

## 14. Criterios de finalización del Master Plan

- [x] Ownership exclusivo de MongoDB claramente establecido (§1, §6, §12).
- [x] Contrato CRUD alineado con `persistence-service.md` sin copiarlo (§4).
- [x] `id` contractual interno diferenciado de `_id` público; transformación ubicada en API (§5).
- [x] Checksum calculado fuera (Extraction) y unicidad garantizada dentro (§3, §6, §7).
- [x] `409 DUPLICATE_CHECKSUM` define cuerpo con documento existente completo (§7).
- [x] No existe `/exists` ni lookup por checksum (§7, §11).
- [x] No existe `Idempotency-Key` (§7).
- [x] Envelope `{code, message}` y catálogo cerrado respetados (§8).
- [x] Sin dependencia con Extraction (§2, §11).
- [x] Compatibilidad directa entre salida de Extraction y entrada de Persistence (§11).
- [x] La decisión de 201-vs-409 tras retry pertenece a API; Persistence solo informa (§7).
- [x] Decisiones pendientes marcadas como pendientes (§13); ninguna convertida en confirmada.
- [x] Trazabilidad de cada capacidad (§9) a la Spec C2 o a `common.md`.

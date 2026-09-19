# Master Plan — Extraction Service

> **Estado:** base de trabajo para crear Issues/Subissues. No es un plan de implementación detallado ni define tareas concretas.
>
> **Fuentes de verdad (no reinterpretar):**
> - `docs/architecture/microservices-alignment-analysis.md` (B1, B2, B3, R3; fronteras §4)
> - `docs/specs/extraction-service.md` (contrato C1 que este servicio provee)
> - `docs/specs/common.md` (checksum, HTTP status, envelope `{code, message}`)
> - `docs/specs/api-service.md` y `docs/specs/persistence-service.md` (solo para entender quién lo consume; no aportan obligaciones a Extraction)
> - `extraction-service-analysis.md` (análisis individual previo)
> - Monolito actual (`app/services/pdf_service.py`, `app/services/checksum.py`) solo como referencia del comportamiento a migrar.

---

## 1. Propósito y alcance

El Extraction Service es un **servicio stateless de procesamiento**: recibe un PDF, extrae su texto, calcula el checksum del contenido y devuelve el resultado. Punto.

**Fuera de alcance (contractual, no negociable):**
- Persistencia de cualquier tipo.
- MongoDB (no accede, no la conoce).
- Persistence Service (no lo llama, no conoce su contrato — B1).
- Orquestación del flujo completo (es de API).
- Reglas de negocio del dominio: unicidad de checksum, límites de filename, IDs.
- Exposición pública (solo API habla con clientes).

## 2. Fuentes y dependencias

**Dependencias de servicio: ninguna saliente.** Extraction solo responde.

| Relación | Dirección | Naturaleza |
|---|---|---|
| API Service | API → Extraction | Único consumidor. Multipart (B3) |
| Persistence Service | — | **No existe relación.** Extraction nunca lo llama |
| Infrastructure | Infra aloja Extraction | Red interna, healthchecks, configuración de ejecución (detalles: Master Plan de Infrastructure) |

## 3. Responsabilidades

1. Recibir el PDF por `multipart/form-data` (campo `file`, filename incluido).
2. Validar la estructura mínima de la request (presencia del campo, contenido).
3. Procesar el contenido como PDF y extraer el texto completo.
4. Calcular **SHA-256 sobre los bytes originales** tal como llegaron.
5. Devolver `{filename, extracted_text, checksum}`.
6. Clasificar sus errores: **input inválido (4xx)** vs **fallo interno (5xx)** — nunca confundirlos (R3).
7. Mantenerse stateless: ningún dato sobrevive a la respuesta.

## 4. Contrato que debe implementar

Resumen de `docs/specs/extraction-service.md` (la Spec manda):

| Aspecto | Contrato |
|---|---|
| Endpoint | `POST /extract` |
| Entrada | `multipart/form-data`, campo `file` (bytes + filename) |
| Salida 200 | `{filename, extracted_text, checksum}` — los tres campos siempre presentes |
| `extracted_text` | string; vacío es válido (PDF sin texto extraíble no es error) |
| `checksum` | según `common.md` §1 (SHA-256, hex, lowercase, 64 chars, sobre los bytes recibidos) |
| Errores | 400 `INVALID_REQUEST` · 422 `INVALID_PDF_CONTENT` · 500 `INTERNAL_ERROR` |
| Envelope de error | `{code, message}` (común, congelado) |
| Garantías | Si 200: checksum corresponde exactamente a los bytes recibidos; cero efectos laterales |

## 5. Contrato que debe consumir

Extraction **no consume contratos de otros servicios**. Lo único que recibe es:

```text
API
 ↓ multipart/form-data (campo file: bytes + filename)
EXTRACTION
```

No depende del contrato interno de Persistence bajo ninguna forma. Su salida la consume API; Extraction no sabe qué pasa después.

## 6. Flujo de extracción

```text
PDF recibido (bytes + filename)
   ↓
validación estructural (¿hay file? ¿bytes no vacíos?)
   ↓  (falla → 400 INVALID_REQUEST)
procesamiento PDF
   ↓  (no procesable como PDF → 422 INVALID_PDF_CONTENT)
   ↓  (fallo interno de procesamiento → 500 INTERNAL_ERROR)
extracción de texto completo
   ↓
cálculo SHA-256 sobre los bytes ORIGINALES
   ↓
200 { filename, extracted_text, checksum }
```

Reglas congeladas:
- El checksum se calcula sobre los **bytes originales recibidos**, sin transformación previa.
- Representación: SHA-256, hexadecimal, minúsculas, 64 caracteres.
- **Extraction produce el checksum; Persistence garantiza su unicidad.** Extraction no verifica ni conoce duplicados.

## 7. Manejo de errores

| Caso | HTTP | code | Clase |
|---|---|---|---|
| Campo `file` ausente o multipart malformado | 400 | `INVALID_REQUEST` | input |
| Contenido no procesable como PDF (corrupto, no-PDF con nombre `.pdf`) | 422 | `INVALID_PDF_CONTENT` | input |
| Fallo interno durante el procesamiento | 500 | `INTERNAL_ERROR` | interno |

Reglas contractuales:
- **415 no es responsabilidad de Extraction** (media type/extensión se valida en API como fail-fast; Extraction recibe bytes y los procesa).
- **409 no corresponde** (no persiste, no detecta duplicados).
- **404 no corresponde** (no administra recursos).
- El sobre siempre es `{code, message}`; `code` es estable y obligatorio; `message` es diagnóstico. El consumidor decide por `status + code`, nunca parseando `message`.
- No se inventan códigos adicionales: el catálogo de Extraction es exhaustivamente estos tres.

## 8. Stateless y fronteras de responsabilidad

- No persiste documentos ni resultados parciales.
- No accede a MongoDB ni a ningún almacenamiento.
- No llama a Persistence ni a ningún otro servicio.
- No mantiene estado de negocio entre requests.
- No garantiza unicidad de checksum.
- No decide el resultado público de la operación completa: su respuesta es un insumo para que API continúe la orquestación.

## 9. Transformaciones y datos

| De | A | Regla |
|---|---|---|
| multipart `file` | bytes en memoria + filename | sin alteración |
| bytes originales | `checksum` | SHA-256 hex lowercase 64 (`common.md` §1) |
| contenido PDF | `extracted_text` | texto completo; vacío si no hay texto extraíble |
| filename recibido | `filename` de salida | devuelto sin modificar |

**No genera** `id` ni `_id`. No agrega campos. No transforma formatos más allá de lo indicado.

## 10. Capacidades a desarrollar

Enumeración funcional (luego se convierten en Issues; sin asignación):

1. **Base del servicio:** skeleton y configuración de ejecución mínima. (Health/liveness/readiness sigue PROPUESTO/PENDIENTE — integration futura, ver §13; no es capacidad congelada de este plan.)
2. **Recepción multipart:** lectura del campo `file` con manejo de tamaño en memoria. El límite de tamaño aplicado hoy (50 MB) vive en API en el borde; este plan no fija ningún límite adicional en Extraction.
3. **Procesamiento PDF:** apertura y lectura del contenido como PDF.
4. **Extracción de texto:** concatenación del texto de todas las páginas.
5. **Cálculo de checksum:** SHA-256 sobre bytes originales según `common.md`.
6. **Clasificador de errores:** distinción input (422/400) vs interno (500) antes de responder; separación entre "no procesable" y "fallé yo" (R3).
7. **Respuesta contractual:** serialización exacta de `{filename, extracted_text, checksum}` y envelope de error `{code, message}`.
8. **Testing:** unitario de procesamiento/checksum, contract tests como proveedor de C1 (casos 200/400/422/500), fixtures de PDFs válidos y corruptos.
9. **Integración:** verificación junto con API del flujo upload completo.

## 11. Orden lógico de implementación

Dependencias lógicas (no cronograma):

```text
1 base/config
   ↓
2 recepción multipart ──▶ 3 procesamiento PDF ──▶ 4 extracción de texto
                                              ╲─▶ 5 checksum
   ↓
6 clasificador de errores ──▶ 7 respuesta contractual (flujo feliz y errores)
   ↓
8 testing (unitario + contract tests C1)  — acompaña cada paso (TDD)
   ↓
9 integración con API (E2E upload)
```

- 3 y 5 pueden avanzar en paralelo una vez que 2 entrega los bytes.
- El endpoint no se considera completo sin el clasificador de errores (422 vs 500 es contractual, no accesorio).
- Los contract tests C1 se escriben contra la Spec, no contra la implementación.

## 12. Integración con los otros servicios

```text
API → Extraction   (única entrada; multipart)
Extraction → API   (respuesta 200 con resultado, o error {code,message})

Extraction ↛ Persistence
Extraction ↛ MongoDB
```

| Servicio | Condición de integración |
|---|---|
| **API** | La salida de Extraction debe ser directamente consumible como `POST /documents` de Persistence (mismos nombres de campo: `filename`, `extracted_text`, `checksum`). Los errores deben traducirse por status+code sin interpretación adicional |
| **Persistence** | Ninguna relación. No importar nada suyo, no conocer su contrato |
| **Infrastructure** | Exponerse solo en red interna; declarar necesidades mínimas: variables de ejecución, healthcheck liveness, límites razonables de memoria dado el tamaño máximo de PDF. Detalles en el Master Plan de Infrastructure |

## 13. Decisiones pendientes (que afectan a Extraction)

Solo se listan; no se resuelven aquí.

1. **Health endpoints:** la convención liveness/readiness sigue PROPUESTA (Alignment §6.6). Hasta su aprobación, implementar liveness mínimo; la ruta exacta queda pendiente.
2. **Valores de timeout aplicados por API hacia Extraction:** pertenecen al Master Plan de API; Extraction solo documenta que su procesamiento puede ser costoso con PDFs grandes.

El límite de tamaño contratado hoy (50 MB) lo aplica API en el borde; un eventual límite defensivo adicional en Extraction es decisión de implementación, no contractual, por lo que no forma parte de este plan.

No hay decisiones nuevas; no hay pendientes bloqueantes.

## 14. Criterios de finalización del Master Plan

Este documento está completo para derivar Issues cuando:

- [x] Cada capacidad de §10 es trazable a la Spec C1 (secciones concretas) o a `common.md`.
- [x] Las decisiones congeladas están reflejadas sin reinterpretación: B1 (sin llamadas salientes), B2 (checksum calculado aquí), B3 (entrada multipart), R3 (422 input / 500 interno), envelope D8.
- [x] El orden lógico (§11) permite empezar por una pieza pequeña y testeable (recepción multipart o checksum).
- [x] No se introdujeron decisiones arquitectónicas nuevas ni se confirmaron las pendientes (§13).
- [x] Nada contradice las Specs de API ni de Persistence.

**Fuera de este documento (a propósito):** clases, módulos, estructura de carpetas, librería de extracción como requisito (la elección se hace en implementación; el monolito usa PyMuPDF como referencia), valores de timeout, Issues, Docker.

# Alignment Arquitectónico — Migración a Microservicios

> **Estado del documento:** ANÁLISIS APROBADO COMO BASE ARQUITECTÓNICA.
> Nada aquí implica implementación, Issues, Specs escritos ni decisión de implementación.
> Este documento **fija fronteras y decisiones arquitectónicas**. Los `/specs` fijarán contratos. Los Master Plans definirán cómo construir cada servicio.
> Fuente de verdad autocontenida: un lector nuevo debe poder comprender la arquitectura resultante sin leer los cuatro informes originales.

---

## 1. Alcance y método

- **Fuentes analizadas:** `api-service-analysis.md`, `extraction-service-analysis.md`, `persistence-analysis.md`, `infrastructure-analysis.md`, código del monolito (`app/`, `infra/`, `tests/`) y configuración actual.
- **Verificación:** las afirmaciones relevantes fueron contrastadas contra el código real del monolito.
- **Estados usados en todo el documento:**
  - **ACTUAL** — así funciona el monolito hoy (hecho verificado en código).
  - **CONFIRMADO** — decisión arquitectónica aprobada por el equipo.
  - **PROPUESTO** — recomendación arquitectónica pendiente de aprobación.
  - **PENDIENTE — BLOQUEA SPECS** — debe resolverse antes de congelar contratos.
  - **PENDIENTE — NO BLOQUEA SPECS** — puede resolverse en specs o Master Plans sin frenar la fase.
  - **POSTERGADO** — explícitamente fuera de v1, con criterio de reevaluación.
- **Identificadores:** `C1–C3` contratos requeridos (§10) · `D1–D11` contradicciones detectadas entre fuentes (§3.2) · `B1–B7` bloqueos (§12).
- **Tres planos separados:** (a) cómo funciona el monolito hoy; (b) qué proponían los informes; (c) qué arquitectura se acuerda/propone finalmente.

---

## 2. Síntesis de los análisis individuales

### API Service (informe)
- Puerta pública; orquesta el upload llamando a Extraction y a Persistence. No extrae, no calcula checksum, no accede a Mongo ni Dragonfly.
- Conserva el contrato público del monolito; propone readiness con verificación de dependencias.
- Riesgos señalados: regex de ObjectId en el contrato público; referencias a Mongo que deben eliminarse de su configuración.

### Extraction Service (informe)
- Recibir bytes del PDF y extraer texto. Su informe originalmente asumía que él llamaría a Persistence (variante "cadena") — **resuelto en contra** por la decisión B1 (§6.2).
- Endpoint `/extract-and-save` descartado por el propio informe como dudoso.

### Persistence Service (informe)
- Único dueño de los datos; único servicio con acceso a Mongo y, potencialmente, a Dragonfly.
- Señala riesgo de doble escritura monolito/Persistence y doble gestión del índice único durante la migración — relevante para el Strangler (§6.10).

### Infrastructure (informe)
- No es servicio de negocio: Traefik, composes, redes, variables, healthchecks, Makefile, estrategia de integración.
- Hallazgos ACTUALES: Traefik vive fuera del repo (reproducibilidad en riesgo); datos de Mongo versionados en `infra/mongodata/`; host público inconsistente entre compose y Makefile; sin healthchecks de aplicación ni `depends_on`.

---

## 3. Comparación y contradicciones

### 3.1 Tabla comparativa (nivel arquitectónico)

| Tema | API | Extraction | Persistence | Infrastructure | Estado |
|---|---|---|---|---|---|
| Responsabilidad | Puerta pública + orquestación | Extraer texto + checksum | Dueño de datos + unicidad | Plataforma | CONFIRMADO (B1, B2) |
| Entrada | multipart del cliente | PDF por multipart desde API | solo JSON desde API | — | CONFIRMADO (B3) |
| Acceso a Mongo | Prohibido | Prohibido | Exclusivo | Aislamiento por red | CONFIRMADO |
| Checksum | No calcula; transporta | Calcula (SHA-256) | Garantiza unicidad | — | CONFIRMADO (B2) |
| Filename | Valida entrada (extensión→415, longitud→422) | No valida | Revalida invariante de longitud (→422) | — | CONFIRMADO (R2) |
| ID de documento | Expone (formato pendiente) | No conoce | Genera (hoy ObjectId) | — | Generación PROPUESTO; formato público PENDIENTE — NO BLOQUEA SPECS |
| Dragonfly | No | No | Cache potencial | Contenedor posible | POSTERGADO (fuera de v1) |
| Errores | Traduce a público (RFC 9457) | Errores internos mínimos | Errores internos mínimos | 502/503 propios del proxy | Formato interno PENDIENTE — NO BLOQUEA SPECS (se define en specs) |
| Health | liveness + readiness (dependencias) | liveness | liveness + readiness (Mongo) | Consume health para orquestar arranque | PROPUESTO (convención liveness/readiness) |

### 3.2 Contradicciones detectadas entre fuentes (D1–D11)

Formato: fuentes en conflicto · evidencia · resolución en este documento.

- **D1. Orquestación.** Informe API: API orquesta ambos. Informes Extraction/Infra: cadena API→Extraction→Persistence. Monolito: sin precedente. → **Resuelto: API orquesta (CONFIRMADO, B1).**
- **D2. Dueño del checksum.** Los tres informes de servicio lo dejaron pendiente con sesgos distintos. → **Resuelto: Extraction calcula; Persistence garantiza unicidad (CONFIRMADO, B2).**
- **D3. Transporte del PDF.** Pendiente multipart vs base64 en los tres informes. → **Resuelto: multipart API→Extraction, JSON API→Persistence (CONFIRMADO, B3).**
- **D4. Validación de filename.** Tres candidatos distintos (API/Extraction/Persistence). Evidencia: extensión se valida en el endpoint (`upload.py:19-22`); longitud máx. 100 en servicio (`pdf_service.py:26`); ambos casos hoy → 415. → **Resuelto (R2):** doble validación (API entrada; Persistence invariante); filename largo → 422; 415 solo para extensión/media type.
- **D5. Formato/validación del ID.** API quiere desacoplar de ObjectId; Persistence sugiere conservar la validación como detalle de Mongo. → Formato público: PENDIENTE — NO BLOQUEA SPECS (v1 conserva ObjectId salvo decisión contraria).
- **D6. Health checks.** API proponía readiness con dependencias; Extraction/Persistence `/health` simple; hoy no existe healthcheck de aplicación. → **PROPUESTO:** convención liveness/readiness (§6.6).
- **D7. Host Traefik.** Compose usa `pdf-extractext.universidad.localhost`; Makefile/README/locustfile usan `api.universidad.localhost` (ambos literales existen en el repo). → PENDIENTE — NO BLOQUEA SPECS; bloquea corte de tráfico (B6).
- **D8. Formato de errores inter-servicios.** API tiende a RFC 9457 unificado; Persistence a mantener; el monolito hoy mezcla RFC 9457 con `{"detail"}`. → PENDIENTE — a resolver en specs (sobre interno mínimo vs RFC 9457 interno).
- **D9. Códigos ante dependencias caídas.** API: 502/503/504 sin decidir; Infra documenta 502/503 de Traefik. → **PROPUESTO:** la aplicación emite 503 (dependencia inalcanzable) / 504 (timeout); 502 queda reservado al proxy. Validar en specs.
- **D10. Puertos internos.** Convención 8000/8001/8002 propuesta por Infra; sin confirmación cruzada. → PENDIENTE — NO BLOQUEA SPECS (Master Plan de Infrastructure).
- **D11. Dragonfly.** Infra lo incluye en el dibujo objetivo; Persistence advierte sobrediseño sin necesidad medida; no existe en código. → **POSTERGADO** (§6.9).

---

## 4. Fronteras de los servicios

### API SERVICE
- **Debe:** exponer el contrato público; validar la entrada (extensión, tamaño, archivo vacío, longitud de filename como validación de ingreso); orquestar el upload llamando primero a Extraction y luego a Persistence; traducir errores internos al contrato público; propagar correlación de requests.
- **NO debe:** extraer texto, calcular checksum, acceder a Mongo o Dragonfly, persistir nada.
- **Conoce:** filename y bytes del PDF (transitorios, en memoria durante la request), respuestas de Extraction y Persistence.
- **Llama a:** Extraction y Persistence. **No llama a:** Mongo, Dragonfly.

### EXTRACTION SERVICE
- **Debe:** recibir bytes del PDF + filename, extraer el texto, calcular el checksum SHA-256 del contenido, devolver `{filename, extracted_text, checksum}`.
- **NO debe:** persistir, acceder a Mongo, exponerse a internet, iniciar llamadas a otros servicios, validar reglas de negocio del dominio.
- **Stateless puro:** no mantiene estado entre requests; ningún resultado sobrevive a la respuesta.
- **No conoce a Persistence.** (Decisión B1.)

### PERSISTENCE SERVICE
- **Debe:** exponer el CRUD interno de documentos; garantizar la unicidad por checksum (rechazo de duplicados); generar el ID del documento; validar los invariantes del dato que persiste (incl. longitud de filename); exponer liveness y readiness.
- **NO debe:** recibir o procesar el PDF binario (recibe solo JSON), extraer texto, validar entrada web, iniciar llamadas a otros servicios.
- **Único servicio con acceso a Mongo.** Ningún otro servicio —ni el monolito tras el corte— escribe en la base.

### INFRASTRUCTURE
- **Pertenece:** routing/TLS (Traefik), composición de contenedores, redes y su aislamiento, variables de entorno, estrategia de healthchecks, volúmenes, observabilidad de plataforma, load testing.
- **NO pertenece:** lógica de negocio, contratos de aplicación, modelos de dominio.
- Los detalles concretos (puertos definitivos, compose, límites, políticas de reinicio) pertenecen al **Master Plan de Infrastructure** — ver §9.

---

## 5. Arquitectura y flujo

### 5.1 Arquitectura resultante (v1)

```
CLIENT
  │  HTTPS (multipart / JSON público)
  ▼
TRAEFIK ───────── routing por host; TLS
  │
  ▼
API SERVICE ────── puerta pública · validación de entrada · orquestación · traducción de errores
  ├──→ EXTRACTION SERVICE   (bytes → extracted_text + checksum; stateless, sin dependencias)
  └──→ PERSISTENCE SERVICE  (único dueño de datos; unicidad por checksum; CRUD)
              │
              ▼
           MONGODB  (solo accesible desde Persistence)
```

**Dragonfly: ausente de v1** (§6.9).

### 5.2 Flujo de upload (paso a paso)

1. **Cliente → API:** `POST /upload-pdf` con el PDF en multipart.
2. **API valida la entrada** (extensión, tamaño, archivo vacío, longitud de filename).
3. **API → Extraction:** reenvía bytes + filename por multipart.
4. **Extraction** extrae el texto y calcula el checksum; devuelve `{filename, extracted_text, checksum}`. No persiste nada.
5. **API → Persistence:** envía `{filename, extracted_text, checksum}` como JSON.
6. **Persistence** persiste garantizando unicidad de checksum; devuelve el documento con su ID.
7. **API responde al cliente** (201 o el error traducido correspondiente).

**Fallo parcial (Extraction OK, Persistence falla):** el resultado de Extraction vive únicamente en memoria dentro de la request de API y se descarta con ella. Como la única escritura durable es el último paso, el fallo es limpio: no hay Saga ni compensación en v1. El retry completo del upload es seguro de punta a punta: si Persistence llegó a insertar, el reintento produce el rechazo por duplicado, sin duplicar datos.

---

## 6. Decisiones arquitectónicas

Formato: problema · alternativas · decisión/propuesta · justificación · estado.

### 6.1 Orquestación — **CONFIRMADO (B1)**
- **Problema:** quién coordina upload (fuentes D1 en conflicto: API orquesta vs cadena Extraction→Persistence).
- **Alternativas:** (A) API orquesta ambos; (B) Extraction llama a Persistence; (C) endpoint combinado.
- **Decisión APROBADA: A.** API conoce a Extraction y Persistence; Extraction y Persistence son servicios hermanos que no se conocen ni se llaman entre sí; Extraction nunca inicia persistencia; Persistence nunca recibe el PDF.
- **Justificación:** mínimo acoplamiento (Extraction queda stateless y sin dependencias); un único punto de traducción de errores y retries; el fallo parcial se resuelve sin Saga (§5.2); la variante B acoplaba Extraction a Persistence y duplicaba niveles de retry.

### 6.2 Checksum — **CONFIRMADO (B2)**
- **Problema:** quién calcula el SHA-256 y quién garantiza la unicidad.
- **Alternativas:** Extraction calcula / Persistence calcula / ambos.
- **Decisión APROBADA:** **Extraction calcula** el SHA-256 del contenido del PDF y lo devuelve en su respuesta; **API lo transporta** sin calcularlo; **Persistence garantiza la unicidad** (rechazo de duplicados). No se prescribe el mecanismo interno de unicidad (la implementación actual del monolito usa índice único en Mongo).
- **Justificación:** solo Extraction posee los bytes; calcularlo en Persistence obligaría a transportar el PDF hasta allí, contradiciendo su contrato JSON; doble cálculo no aporta nada.

### 6.3 Transporte del PDF — **CONFIRMADO (B3)**
- **Problema:** cómo viajan los bytes API→Extraction.
- **Alternativas:** multipart/form-data vs JSON+Base64.
- **Decisión APROBADA:** **multipart/form-data** entre API y Extraction; **application/json** entre API y Persistence. No se usa base64 como mecanismo contractual.
- **Justificación:** base64 agrega ~33% de volumen y una copia extra en memoria; multipart ya es el mecanismo del contrato público actual y admite streaming.

### 6.4 Filename — **CONFIRMADO (R2)**
- **Evidencia ACTUAL (verificada):** extensión inválida → **415** (`upload.py:19-22`); filename demasiado largo (`FilenameTooLongError`, límite 100 en `pdf_service.py:26`) → también **415** en el monolito (`upload.py:53-57`, vía `ValueError` genérico).
- **Decisión APROBADA (R2):**
  - Filename demasiado largo → **422 Unprocessable Content**, tanto en el contrato público (API) como en la revalidación de Persistence (salvo futura decisión explícita en contrario).
  - **415 queda reservado exclusivamente a extensión/media type no soportado.**
  - Doble validación: API valida en el borde (fail-fast); Persistence revalida el invariante como dueño del dato.
- **Justificación:** 415 describe media type, no la violación de una regla de un campo; 422 separa "formato del payload" de "campo inválido" y es coherente con el 422 que ya emite la validación de esquemas. Es un **cambio contractual explícito** respecto del monolito (415 → 422 para filename largo).

### 6.5 ID del documento
- **ACTUAL:** el ID es un **ObjectId generado por Mongo** y se expone tal cual en el contrato público (validado por regex en la API del monolito).
- **PROPUESTO:** la generación del ID es responsabilidad de Persistence (hoy delegada en Mongo; sin cambio de comportamiento en v1).
- **PENDIENTE — NO BLOQUEA SPECS:** formato público del ID (seguir exponiendo ObjectId vs formato neutral). v1 conserva ObjectId salvo decisión contraria; puede revisarse sin frenar specs ni implementación.

### 6.6 Errores y health — **PROPUESTO / PENDIENTE en specs**
- **Errores (PROPUESTO):** RFC 9457 unificado en el borde público; entre servicios, un sobre de error mínimo; API es el único traductor interno→público; la aplicación emite 503 (dependencia inalcanzable) / 504 (timeout) y **502 queda reservado al proxy**. El formato exacto del sobre interno — y si los contratos internos usan RFC 9457 — es **PENDIENTE — NO BLOQUEA SPECS** (se define dentro de los propios specs).
- **PDF corrupto/no procesable — CONFIRMADO (R3):** en el monolito hoy produce 415 (vía el mismo `ValueError` genérico de `upload.py:53-57`). **Decisión APROBADA:** contenido no procesable como PDF → **422 Unprocessable Content**; 415 queda reservado a extensión/media type. **Extraction detecta y clasifica** (es quien ejecuta la extracción) y debe distinguir: error atribuible al input → 4xx de cliente; fallo interno del procesamiento → 5xx. API traduce esa clasificación al contrato público. No confundir PDF corrupto con fallo interno de Extraction. Cambio contractual explícito respecto del monolito (415 → 422).
- **Health (PROPUESTO):** convención **liveness** (`/health`: proceso vivo, sin verificar dependencias) y **readiness** (`/health/ready`: verifica las dependencias necesarias para atender tráfico — Mongo en Persistence; Extraction y Persistence en API). Extraction, sin dependencias, solo necesita liveness.

### 6.7 Retries y timeouts — **PROPUESTO (principio); valores en Master Plan de API**
- **Principios PROPUESTOS:**
  - Retries **centralizados en API**; ningún reintento entre Extraction/Persistence ni hacia Mongo a nivel aplicación (no hay retries distribuidos).
  - No reintentar errores funcionales (4xx ya parseados); solo errores de transporte.
  - Sin compensación/Saga en v1 (§5.2).
- **Idempotencia (precisión contractual):** `POST /documents` **no es HTTP-idempotente** (1ª llamada → 201, reintento → 409), pero tiene **efecto acotado por la garantía de unicidad**: repetirlo nunca duplica datos. La recuperación transparente tras un 409 post-retry (consulta por checksum vs incluir el recurso en la respuesta 409) es **PENDIENTE — se define en specs**.
- **`Idempotency-Key`: NO se propone en v1** — el checksum actúa como clave natural (el reintento del mismo contenido produce el mismo checksum). Revalorable en una evolución posterior.
- **Valores numéricos** (cantidad de reintentos, timeouts por llamada, backoff): **fuera del Alignment** → Master Plan de API.

### 6.8 Modelo PDFDocument — **PROPUESTO**
- Los servicios **no comparten código ni clases**: comparten únicamente los contratos JSON definidos en specs. Persistence es dueño del modelo persistido; API dueña de sus DTOs públicos; Extraction no conoce el documento completo. Sin librería compartida en v1 (evita acoplamiento y versionado cruzado).

### 6.9 Dragonfly — **POSTERGADO**
- **Decisión de alcance:** **Dragonfly queda fuera de v1 y se reevaluará posteriormente en función de evidencia de rendimiento** (load testing sobre la arquitectura nueva). No existe en el código actual y ninguna fuente documenta un problema medido que resuelva; incorporarlo ahora sería sobrediseño.

### 6.10 Strangler (estrategia de migración) — **PROPUESTO**
- **Construcción en paralelo:** los microservicios se construyen y verifican internamente mientras el monolito sigue siendo el único backend público y el único escritor de Mongo.
- **Corte de tráfico:** cuando el flujo E2E interno esté verde de forma sostenida, Traefik conmuta el host público del monolito al API Service; el corte es **total por host** (el contrato público completo migra a la vez). El monolito queda en stand-by como mecanismo de rollback.
- **Post-corte:** se retira el acceso a Mongo del monolito y luego se depreca.
- **Riesgo gobernado:** durante la convivencia debe existir un solo escritor/gestor de la base a la vez (señalado por el informe de Persistence).
- El procedimiento operativo detallado (ventanas, criterios de go/no-go) pertenece al Master Plan de Infrastructure.

---

## 7. Ownership de datos y responsabilidades

| Dato | API | Extraction | Persistence | Base de datos |
|---|---|---|---|---|
| filename | valida entrada, transporta | transporta | **dueño**: valida invariante, persiste | persiste |
| PDF bytes | recibe y reenvía (transitorio) | procesa (transitorio, sin persistir) | nunca llega | nunca |
| extracted_text | transporta | **crea** | persiste | persiste |
| checksum | transporta (no calcula) | **crea** (SHA-256) | garantiza unicidad | mecanismo de unicidad |
| document ID | expone (formato pendiente) | no conoce | **crea** | genera (hoy ObjectId) |
| created_at / updated_at | — | — | **No existen hoy** — PENDIENTE — NO BLOQUEA SPECS | — |

La tabla define quién crea, valida, transporta, persiste y expone cada dato; los specs fijarán la representación exacta.

---

## 8. Principios de testing

Niveles requeridos (sin fijar librerías, fixtures ni estrategias — eso pertenece a los Master Plans):

- **Unitarios:** lógica de cada servicio aislada (extracción, checksum, validaciones, mapeos, traducción de errores).
- **Contract tests:** contra los specs C1/C2/C3, a ambos lados de cada contrato (proveedor y consumidor).
- **Integración:** cada servicio contra sus dependencias reales o simuladas según su Master Plan (Persistence contra base real preservando la práctica actual del monolito).
- **E2E:** upload → extract → documents → base, a través del routing, antes del corte de tráfico.
- **Infrastructure/smoke:** routing, healthchecks, aislamiento de la base (ningún servicio distinto de Persistence alcanza Mongo).
- **Performance:** reusar los tests de carga existentes (k6/Locust del monolito, ACTUALES) sobre la arquitectura nueva; su resultado es el insumo para reevaluar Dragonfly.

Los tests del monolito no se copian ciegamente: los de extracción/checksum migran conceptualmente a Extraction; los de repositorio a Persistence; los de orquestación se rediseñan en API; los de API del monolito se cubren con contract tests + E2E.

---

## 9. Principios de infraestructura

Principios arquitectónicos (los detalles pertenecen al **Master Plan de Infrastructure**):

- **Un proceso por servicio**, cada uno tras el routing de Traefik; solo API recibe tráfico público.
- **Mongo no expuesto**: accesible únicamente por Persistence; la topología de red debe impedir el acceso directo desde API/Extraction.
- **Healthchecks como puerta de arranque:** liveness/readiness por servicio (§6.6); la orquestación de arranque se basa en readiness.
- **Reproducibilidad:** la infraestructura (incl. Traefik) debe poder reconstruirse desde fuentes versionadas o documentadas; hoy Traefik está fuera del repo (riesgo ACTUAL).
- **Persistencia de datos:** el volumen de la base no debe versionarse en el repo (hoy `infra/mongodata/` contiene datos versionados — riesgo ACTUAL).
- **Observabilidad mínima:** correlación de requests (`X-Request-ID` ya existe en el monolito), logs por servicio y health endpoints consumibles.
- **Un solo host público**, definido y documentado (pendiente D7).
- Puertos, `depends_on`, restart policies, resource limits, versión de Mongo y estrategia TLS: **Master Plan de Infrastructure**.

---

## 10. Inventario de contratos requeridos

> Los contratos definitivos (schemas exactos, ejemplos, headers, códigos finales, formatos) se definen y congelan en **`/specs`**. Esta sección solo enumera qué contratos deben existir, quién los provee, quién los consume y qué decisiones pendientes afectan a cada uno.

| Contrato | Proveedor | Consumidor | Contenido de alto nivel | Pendientes que lo afectan |
|---|---|---|---|---|
| **C1 — Extracción** | Extraction | API | `POST` del PDF en multipart (B3) → `{filename, extracted_text, checksum}` (B2). Errores de entrada y de procesado: 415 solo media type; 422 para contenido no procesable (R3); distinción 4xx/5xx (R3). Health | Ninguno bloqueante; formato del sobre de errores interno (D8) |
| **C2 — Documentos** | Persistence | API (**único**) | CRUD JSON de documentos; garantía de unicidad por checksum (rechazo de duplicados); generación de ID. Validación de invariantes: filename largo → 422 (R2). Health liveness/readiness | Semántica del 409 tras retry (§6.7); formato público del ID (§6.5); paginación de listados |
| **C3 — API pública** | API | Clientes externos | Conserva el contrato público ACTUAL del monolito (upload + CRUD), más health liveness/readiness. Errores públicos RFC 9457 + 503/504 ante dependencias. **Cambio contractual explícito:** filename largo → 422 y PDF corrupto → 422 (hoy 415); 415 solo media type (R2/R3) | RFC 9457 unificado (§6.6); formato público del ID (§6.5) |

Reglas: ningún cuarto contrato está justificado hoy; `GET /documents/exists` es una **alternativa pendiente** (no un endpoint aprobado) para resolver el 409 post-retry.

---

## 11. Decisiones pendientes priorizadas

### PENDIENTE — BLOQUEA SPECS
**Ninguno.** R2 (§6.4: filename largo → 422) y R3 (§6.6: PDF corrupto → 422, con distinción 4xx/5xx en Extraction) fueron aprobados por el equipo. Los specs pueden redactarse completo.

### PENDIENTE — NO BLOQUEA SPECS (se definen dentro de specs o en Master Plans)
1. Formato del sobre de errores interno / RFC 9457 entre servicios (D8) — dentro de las specs.
2. Resolución del 409 post-retry: consulta por checksum vs recurso incluido en la respuesta (§6.7) — dentro de C2.
3. Formato público del ID (D5/§6.5).
4. Paginación de listados.
5. Puertos internos (D10) y demás detalles de plataforma — Master Plan de Infrastructure.
6. `created_at` / `updated_at` (hoy inexistentes).

### POSTERGADO
7. **Dragonfly** — fuera de v1; reevaluación con evidencia de rendimiento (§6.9).
8. Upgrade de la versión de Mongo (la actual está fuera de soporte) — Master Plan de Infrastructure.
9. IDs neutrales, observabilidad avanzada, reubicación de Traefik/TLS real — Master Plan de Infrastructure.

---

## 12. Blockers

### A. Bloqueantes de arquitectura
**Estado: resueltos.** B1 (orquestación), B2 (checksum), B3 (transporte), R2 (filename largo → 422) y R3 (PDF corrupto → 422 con distinción 4xx/5xx) fueron **aprobados por el equipo** (§6.1–6.4, §6.6). No quedan pendientes que bloqueen specs; la siguiente compuerta es la aprobación de los specs C1–C3.

### B. Bloqueantes de integración/deployment (no frenan specs ni implementación; frenan el corte de tráfico)
| # | Bloqueo | Por qué es de deployment |
|---|---|---|
| B5 | Traefik fuera del repo, no reproducible | La comunicación interna no depende de Traefik; afecta la repetibilidad del corte. Master Plan de Infrastructure |
| B6 | Host público inconsistente (D7) | Configuración de edge; los servicios son agnósticos al host |
| B7 | Routing externo/TLS sin definir | Condición del edge; deadline = corte de tráfico |

**Regla práctica:** los bloqueantes de arquitectura ya no frenan el trabajo de specs; los pendientes del §11 frenan solo la congelación final de los contratos afectados. B5–B7 se trabajan en la pista de Infrastructure en paralelo.

---

## 13. Resultado del Alignment

### CONFIRMADO (aprobado o verificado)
- **B1:** API orquesta; Extraction y Persistence son hermanos y no se conocen entre sí.
- **B2:** Extraction calcula el checksum SHA-256; Persistence garantiza la unicidad; API no calcula.
- **B3:** multipart/form-data (API→Extraction) y application/json (API→Persistence).
- **R2:** filename demasiado largo → **422** (público y en revalidación de Persistence); **415 reservado a extensión/media type**; doble validación API (borde) + Persistence (invariante).
- **R3:** PDF corrupto/no procesable → **422**; 415 solo media type; Extraction detecta y clasifica input-error (4xx) vs fallo interno (5xx); API traduce.
- **Solo Persistence accede a Mongo** (acuerdo unánime de las cuatro fuentes).
- Hechos ACTUALES verificados en el monolito: contrato público completo (upload + CRUD con 201/204/400/404/409/413/415/422); checksum SHA-256 sobre bytes; ID=ObjectId de Mongo; extracción de texto existente; sin healthchecks de aplicación; Dragonfly inexistente; Traefik fuera del repo; datos de Mongo versionados en el repo; filename largo y PDF corrupto → **415 hoy** (R2/R3 los cambian a 422 contractualmente).

### PROPUESTO (pendiente de aprobación del equipo)
- RFC 9457 unificado en borde + sobre de error interno mínimo; 503/504 en API, 502 reservado al proxy.
- Convención liveness/readiness.
- Principios de retries: centralizados en API, sin retries distribuidos, sin reintentar 4xx, sin Saga en v1.
- Sin código compartido entre servicios; contratos como única frontera común.
- Estrategia Strangler: construcción en paralelo, corte total por host, monolito en stand-by, retiro progresivo.

### POSTERGADO
- **Dragonfly fuera de v1**, reevaluable con evidencia de rendimiento. Upgrade de Mongo, IDs neutrales, TLS real, observabilidad avanzada.

### Secuencia de trabajo resultante (dependencias lógicas, no plan operativo)
`Alignment (este documento) → Specs C1–C3 → Master Plans (API, Extraction, Persistence, Infrastructure) → Issues → Implementación`

- Las specs dependen de este documento; no quedan pendientes que las bloqueen.
- Los Master Plans dependen de las specs aprobadas; entre sí pueden avanzar en paralelo donde no compartan contrato.
- B5–B7 solo bloquean el corte de tráfico, no las fases anteriores.

---

## Notas finales

- **INFORMACIÓN INSUFICIENTE:** ubicación/configuración real del Traefik externo; DNS real del host; umbrales de performance objetivo (insumo para la futura decisión de Dragonfly).
- Las referencias de código citadas (`upload.py`, `pdf_service.py`, `pdf_repository.py`, `checksum.py`, `pdfs.py`) describen el monolito ACTUAL como evidencia; no prescriben implementación de los servicios nuevos.

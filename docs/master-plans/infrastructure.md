# Master Plan — Infrastructure

> **Estado:** base de trabajo para crear Issues/Subissues. No es un plan de implementación detallado ni una lista de Issues.
>
> **Fuentes de verdad y jerarquía de autoridad:** `docs/architecture/microservices-alignment-analysis.md` → `docs/specs/*.md` → `infrastructure-analysis.md` → configuración actual del repo (solo como evidencia del punto de partida; nunca convierte un valor existente en decisión arquitectónica).
>
> Decisiones CONFIRMADAS que gobiernan este documento: B1 (API orquesta), B2 (checksum en Extraction), B3 (multipart/JSON), solo Persistence accede a MongoDB, Dragonfly fuera de v1, corte Strangler por host con rollback.

---

## 1. Propósito y alcance

Infrastructure proporciona el **entorno de ejecución y conectividad** de la arquitectura: orquestación de contenedores, Traefik, redes, exposición pública, conectividad interna, MongoDB como dependencia desplegada, persistencia de datos, configuración por variables de entorno, aislamiento, y facilidades de healthchecks/observabilidad.

**Fuera de alcance (contractual):** lógica de negocio, endpoints y contratos, extracción de PDF, checksum, CRUD de documentos, reglas de dominio, acceso de API o Extraction a MongoDB, retries de negocio de API. Infrastructure **no asume ownership funcional de Persistence** ni de ningún servicio: gestiona su entorno, no su comportamiento.

## 2. Fuentes y dependencias

```text
                    ┌──────────────┐
                    │   Traefik    │   (entrypoint público)
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │ API Service  │
                    └──────┬───────┘
                 ┌─────────┴─────────┐
                 ▼                   ▼
        ┌────────────────┐   ┌─────────────────┐
        │   Extraction   │   │   Persistence   │
        └────────────────┘   └────────┬────────┘
                                      ▼
                                ┌───────────┐
                                │  MongoDB  │
                                └───────────┘
```

Reglas del grafo:

- Traefik → API es la **única** exposición pública.
- API → Extraction y API → Persistence son comunicación interna.
- Persistence → MongoDB es comunicación interna exclusiva.
- API ↛ MongoDB; Extraction ↛ MongoDB; Extraction ↛ Persistence.
- Traefik no es dueño de datos; MongoDB **funcionalmente** pertenece a Persistence, aunque Infrastructure gestione su despliegue/almacenamiento (distinción ownership funcional vs. responsabilidad operacional, §12).

## 3. Responsabilidades de Infrastructure

1. Entorno de ejecución de los cuatro componentes (api, extraction, persistence, mongodb).
2. Traefik como reverse proxy y entrypoint público único.
3. Conectividad API → Extraction y API → Persistence.
4. Conectividad Persistence → MongoDB.
5. Aislamiento de MongoDB frente a API/Extraction.
6. Redes Docker necesarias para esa topología.
7. Persistencia del almacenamiento de MongoDB independiente del ciclo de vida del contenedor.
8. Configuración externa por variables de entorno (sin secretos versionados).
9. Separación configuración ↔ código de aplicación.
10. Facilitar liveness/readiness **cuando la convención sea aprobada** (pendiente — §13).
11. Resolución de nombres/hosts del entorno local.
12. Reproducibilidad: entorno reconstruible desde fuentes versionadas (hoy Traefik está fuera del repo — riesgo ACTUAL, B5 del Alignment).
13. Integración de las imágenes de los tres servicios.
14. Ruta de despliegue clara Traefik → API.

## 4. Topología de ejecución

```text
Internet/Cliente
       │
       ▼
    Traefik        ← público
       │
       ▼
      API          ← público (solo vía Traefik)
     /   \
    ▼     ▼
Extraction Persistence   ← internos, jamás expuestos
              │
              ▼
           MongoDB       ← interno + almacenamiento persistente
```

| Capa | Componentes | Visibilidad |
|---|---|---|
| Pública | Traefik | Internet/LAN del proyecto |
| Borde | API | Solo vía Traefik |
| Interna | Extraction, Persistence | Solo red interna |
| Datos | MongoDB | Solo desde Persistence |

Puertos finales, nombres y hosts: **pendientes** (D7/D10); la convención propuesta 8000/8001/8002 queda como referencia no congelada.

## 5. Traefik y exposición pública

Comportamiento arquitectónico esperado:

- Recibe el tráfico público y enruta **únicamente** al API Service.
- Termina TLS donde el entorno lo requiera.
- Preserva/propaga headers relevantes, incluido `X-Request-ID`.
- No expone Extraction, ni Persistence, ni MongoDB.

Referencia del estado actual (**no decisión**): compose actual usa `traefik` externo al repo, host `pdf-extractext.universidad.localhost`, red externa `red_compartida_pdf` con `external: true`. El Makefile/README/locustfile usan otro host (`api.universidad.localhost`) — inconsistencia documentada (D7/B6). Nada de esto es definitivo hasta que se resuelvan los pendientes de §13.

## 6. Redes y conectividad

Matriz mínima de conectividad (✓ = requerido, ✗ = prohibido):

| Origen \ Destino | API | Extraction | Persistence | MongoDB |
|---|---|---|---|---|
| Traefik | ✓ | ✗ | ✗ | ✗ |
| API | — | ✓ | ✓ | ✗ |
| Extraction | — | — | ✗ | ✗ |
| Persistence | — | — | — | ✓ |

La segmentación se mantiene simple: la regla arquitectónica es el aislamiento de MongoDB y la no-exposición de los servicios internos. Nombres de red, aliases y cantidad exacta de redes son detalle de implementación/Issues.

## 7. MongoDB y persistencia de datos

- Infrastructure provee MongoDB como **dependencia operacional** de Persistence.
- Almacenamiento persistente independiente del ciclo de vida del contenedor.
- **Persistence es el único servicio autorizado** a acceder.
- Infrastructure administra el volumen/almacenamiento, **nunca** el modelo de dominio (colecciones, campos, índices, reglas: eso es de Persistence).
- **RIESGO ACTUAL:** `infra/mongodata/` contiene datos versionados en el repo. Es un problema de infraestructura/configuración a corregir posteriormente (estrategia exacta: pendiente — §13); no es un comportamiento deseado ni una decisión a preservar.

## 8. Configuración y secretos

- Todo acoplamiento se expresa por variables de entorno (URLs internas de servicios, conexión a MongoDB, configuración de Traefik). Los nombres concretos que ya usan los servicios salen de las Specs/AGENTS; no se inventan aquí.
- Separación estricta: configuración fuera del código; valores por defecto seguros para desarrollo; **ningún secreto versionado ni hardcodeado** (el `.env` actual del monolito está commiteado — riesgo a tratar en Issues de Infra).
- Tres clases de valores: configuración de desarrollo (versionable, segura), configuración sensible (nunca versionada), y defaults seguros.

## 9. Healthchecks, disponibilidad y ciclo de vida

**Capacidad pendiente de alineación, no congelada.** Lo que Infrastructure debe resolver conceptualmente:

- El arranque ordenado necesita distinguir **liveness** (proceso vivo) de **readiness** (listo para tráfico; en Persistence incluye MongoDB, en API incluye sus dependencias) — la convención exacta sigue PROPUESTA (Alignment §6.6).
- La dependencia de arranque entre servicios (p. ej. `depends_on`) se evaluará cuando la convención de health se apruebe.
- MongoDB hoy sí tiene healthcheck (docker-compose.db.yml); los servicios de aplicación no tienen ninguno (ACTUAL).

No fijar aquí: rutas, códigos, profundidad de readiness, políticas de retry, timeouts ni `depends_on` concretos.

## 10. Observabilidad y operación

Alcance mínimo de Infrastructure (sin introducir herramientas no aprobadas):

- Logs de contenedores accesibles con identificación clara por servicio.
- Estado de contenedores y diagnóstico de conectividad entre servicios y hacia MongoDB.
- Visibilidad básica de Traefik (dashboard/routing).
- Soporte a la trazabilidad: garantizar que `X-Request-ID` atraviese el proxy.

Sin observabilidad avanzada en v1 (métricas/tracing distribuido: evaluable post corte, Alignment §6.9-adyacente).

## 11. Integración con los tres servicios

| Servicio | Condiciones que Infrastructure debe garantizar |
|---|---|
| **API** | Único alcanzable desde Traefik; conectividad a Extraction y Persistence; sin ruta a MongoDB |
| **Extraction** | Alcanzable solo por API; no público; sin ruta a MongoDB ni a Persistence |
| **Persistence** | Alcanzable solo por API; conectividad exclusiva a MongoDB |
| **MongoDB** | Solo desde Persistence; almacenamiento persistente; nunca público |

## 12. Fronteras y ownership

| Elemento | Responsable funcional | Responsable operacional |
|---|---|---|
| API Service | API | Infrastructure (runtime) |
| Extraction Service | Extraction | Infrastructure (runtime) |
| Persistence Service | Persistence | Infrastructure (runtime) |
| Documentos/dominio | Persistence | — |
| MongoDB/datos | Persistence | Infrastructure (despliegue/volumen) |
| Traefik | Infrastructure | Infrastructure |
| Redes | Infrastructure | Infrastructure |
| TLS/entrypoint | Infrastructure | Infrastructure |

"Responsable operacional" nunca implica decidir comportamiento funcional.

## 13. Decisiones pendientes

Solo se listan; **ninguna se resuelve aquí**:

1. Host público definitivo (D7/B6 — inconsistencia compose vs Makefile).
2. Traefik: reproducibilidad (fuera del repo — B5) y configuración final/TLS (B7).
3. Convención de health liveness/readiness y su uso en orquestación de arranque (Alignment §6.6 — PROPUESTO).
4. 503/504 ante dependencias (D9 — PROPUESTO, afecta contratos públicos).
5. Puertos definitivos y nombres de servicios/redes (D10).
6. Estrategia para `infra/mongodata/` (datos versionados) y volumen definitivo.
7. Manejo del `.env` versionado y gestión de secretos.
8. Versión de MongoDB (4.4 EOL — POSTERGADO; evaluar en su momento).
9. Timeouts/retries a nivel de plataforma — definición posterior.

## 14. Criterios de finalización del Master Plan

- [x] Topología de ejecución definida (§4).
- [x] API establecido como único entrypoint público (§4–§5).
- [x] Extraction y Persistence no expuestos públicamente (§4, §6).
- [x] MongoDB no expuesto públicamente (§4, §6).
- [x] Persistence como único acceso a MongoDB (§2, §7, §12).
- [x] Redes y conectividad entre componentes definidas a nivel de principio (§6).
- [x] Persistencia de datos de MongoDB contemplada (§7).
- [x] Configuración externa contemplada (§8).
- [x] Traefik contemplado sin congelar valores pendientes (§5).
- [x] Healthchecks tratados como pendientes (§9).
- [x] Riesgo de `infra/mongodata/` identificado (§7).
- [x] Ownership funcional vs operacional separado (§12).
- [x] Sin responsabilidades de negocio introducidas (§1).
- [x] Sin decisiones pendientes cerradas (§13).
- [x] El documento permite derivar Issues/Subissues posteriormente (capacidades por sección: topología, Traefik, redes, almacenamiento, configuración, health cuando se apruebe, observabilidad mínima).

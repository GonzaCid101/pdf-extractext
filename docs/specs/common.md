# Spec Común — Convenciones contractuales compartidas

> Alcance: reglas que más de un contrato debe respetar de forma idéntica. No es una copia del Alignment; no prescribe implementación interna (frameworks, clases, librerías, estructura de carpetas quedan en los Master Plans).
> Trazabilidad: materializa las decisiones CONFIRMADAS del Alignment §6 (B1–B3, R2, R3) y las convenciones referenciadas por C1, C2 y C3.

---

## 1. Checksum

Regla única en los tres contratos:

| Propiedad | Valor |
|---|---|
| Algoritmo | SHA-256 |
| Entrada | bytes crudos del archivo PDF, exactamente como fueron recibidos |
| Representación | hexadecimal, lowercase |
| Longitud | 64 caracteres |
| Productor | Extraction (único que lo calcula) |
| Consumidores | API lo transporta sin modificarlo; Persistence lo persiste y garantiza su unicidad |

Ningún otro servicio recalcula ni reinterpreta el checksum. Una discrepancia de formato entre servicios es una violación de contrato.

## 2. Taxonomía de errores y HTTP status

Regla de asignación de códigos, idéntica en todos los contratos:

| Código | Significado contractual | Cuándo se usa |
|---|---|---|
| 400 | Request estructuralmente inválida | Falta una parte requerida del mensaje, payload vacío donde se exige contenido, cuerpo malformado |
| 404 | Recurso inexistente | El recurso identificado no existe |
| 409 | Conflicto de estado | La operación colisiona con el estado actual (p. ej. checksum duplicado) |
| 415 | Media type no soportado | **Exclusivamente** extensión/media type no admitido. Nunca para contenido ni reglas de datos |
| 422 | Contenido no procesable / regla de dato violada | Un valor sintácticamente válido viola el contrato (p. ej. filename demasiado largo, PDF no procesable) |
| 5xx | Fallo interno del servicio | El servicio no pudo completar una operación válida (500 genérico; 503 dependencia inalcanzable; 504 timeout de dependencia) |

Separación obligatoria:

- **Errores de input (4xx):** atribuibles al consumidor del contrato. No se reintentan automáticamente.
- **Conflictos (409):** estado, no input: el mensaje era válido, el estado lo rechaza.
- **Errores internos (5xx):** atribuibles al servicio o sus dependencias. Nunca se exponen al cliente público con detalle interno.

Los servicios internos **distinguen conceptualmente** "input inválido" de "fallo interno" ya en su propia respuesta: API debe poder traducir sin reinterpretar (Alignment R3). El formato del cuerpo de error entre servicios está congelado en §3 (envelope `{code, message}`).

## 3. Formato de errores

### Errores internos (servicio → servicio) — CONGELADO (D8)

Envelope contractual obligatorio en toda respuesta de error entre servicios:

```json
{
  "code": "ERROR_CODE",
  "message": "diagnostic message"
}
```

- `code` — **obligatorio, estable.** Identificador de causa (p. ej. `INVALID_PDF_CONTENT`, `INTERNAL_ERROR`, `FILENAME_TOO_LONG`, `DUPLICATE_CHECKSUM`). Cada servicio documenta solo el catálogo de códigos que puede producir, en su propia Spec.
- `message` — **obligatorio, diagnóstico.** Nunca se usa como señal de lógica de negocio; API traduce mediante `status + code`, nunca parseando `message`.
- El **HTTP status es la señal primaria de clase** (4xx input / 409 conflicto / 5xx interno); `code` desambigua causas dentro de la misma clase.
- **No** se agregan campos adicionales en v1 (sin `details`). **No** se usa RFC 9457 como envelope interno.

### Errores públicos (API → cliente)

Formato RFC 9457 (`application/problem+json`) sigue **PENDIENTE** de aprobación (Alignment §6.6). Mientras tanto, las tablas de códigos de cada Spec son contractuales y el formato del cuerpo público se congela cuando esa decisión se apruebe. No bloquea las tablas de códigos.

## 4. Identificación de recursos — CONGELADO (v1)

- **Formato v1:** ObjectId hexadecimal de 24 caracteres (heredado del monolito).
- **Quién genera:** Persistence, al persistir el documento.
- **Nombres de campo por contrato (diferencia deliberada, no es discrepancia):**
  - **Persistence usa `id`** en sus responses (modelo interno).
  - **API expone `_id`** en el contrato público, por compatibilidad con el monolito y para no modificar clientes durante el corte Strangler.
  - **API realiza la transformación `id` (Persistence) → `_id` (público)**. No se exponen simultáneamente `id` y `_id`.
- El formato público a largo plazo (ObjectId vs formato neutral) sigue POSTERGADO; v1 = ObjectId.

## 4.1 Semántica del 409 por checksum duplicado — CONGELADO

Cuando Persistence rechaza un `POST /documents` por checksum duplicado:

- responde **409**;
- el **cuerpo contiene la representación completa del documento existente**;
- código interno: `DUPLICATE_CHECKSUM`.

Esto habilita la recuperación tras retry: si el 201 original se pierde, el retry obtiene 409 + documento y API completa la operación pública como éxito. **No existe** endpoint `/exists` ni lookup por checksum; **no** hay `Idempotency-Key` ni almacenamiento de idempotencia en v1.

## 5. Convenciones HTTP generales

- Comunicación interna: HTTP/JSON entre servicios, multipart/form-data solo para el transporte del PDF hacia Extraction (decisión B3).
- Correlación: header `X-Request-ID` propagado a lo largo de la cadena de llamadas (existe en el monolito actual; los servicios nuevos deben respetarlo y propagarlo).
- Los contratos no fijan timeouts, cantidades de reintentos ni backoff: eso pertenece al Master Plan de API (principio del Alignment: retries centralizados en API, solo ante errores de transporte).

## 6. Regla de lectura de estas Specs

Las Specs definen **qué** debe cumplir cada servicio: endpoints, payloads, códigos, invariantes. Cualquier decisión sobre **cómo** (librería HTTP, framework, lenguaje interno, clases, estructura de carpetas, Docker) está fuera de alcance y pertenece al Master Plan correspondiente.

# PDF Extractext

## Integrantes

- Gonzalo Cid
- Manuel Andres Perez
- Juan Manuel De Los Rios
- Bruno Alcaraz

## Introducción

API REST para extraer texto de archivos PDF y almacenarlos en MongoDB. Permite subir documentos, extraer su contenido textual, generar checksums SHA-256 para verificación de integridad de datos y gestionar los documentos almacenados mediante operaciones CRUD completas.

## Características principales

- **Procesamiento 100% en memoria** — sin archivos temporales en disco
- **Extracción de texto** de archivos PDF usando PyMuPDF
- **Generación de checksums SHA-256** para verificación de integridad
- **Almacenamiento en MongoDB** con Motor (driver asíncrono)
- **API REST con FastAPI** y documentación automática Swagger UI
- **Arquitectura en capas con núcleo de dominio y puertos/adaptadores**
- **Configuración centralizada** mediante variables de entorno

## Tecnologias

Python 3.14.0 | FastAPI | Pydantic | PyMuPDF | Motor | MongoDB | Docker | Pytest

## Requisitos

| Componente | Versión |
|---|---|
| Docker | 20.10+ |
| Docker Compose | 2.0+ |
| GNU Make | Instalado por defecto en Linux/macOS (usar Make for Windows si aplica) |

## Instalación y Configuración

### Opción 1: Todo con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone <https://github.com/GonzaCid101/pdf-extractext>
cd pdf-extractext

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Construir la imagen de la API
make build

# 4. Levantar DB + API
make up
```
La API estará disponible en:
- **API:** http://localhost:8000
- **Documentación interactiva:** http://localhost:8000/docs

### Opción 2: MongoDB en Docker + app local con uv

```bash
# 1. Clonar el repositorio
git clone <https://github.com/GonzaCid101/pdf-extractext>
cd pdf-extractext

# 2. Configurar variables de entorno
cp .env.example .env
# Cambiar MONGO_URI a mongodb://localhost:27017/ en .env

# 3. Levantar solo MongoDB (puerto 27017 expuesto)
make db-up

# 4. Instalar dependencias y ejecutar
uv sync
uv run python -m app.main
```
La API estará disponible en:
- **API:** http://localhost:8000
- **Documentación interactiva:** http://localhost:8000/docs

* Comandos Útiles (Makefile)
```bash
# Levantar DB + API
make up

# Levantar solo la base de datos
make db-up

# Detener contenedores
make down

# Detener solo la base de datos
make db-down

# Abrir docs en el navegador
make docs
```
Validamos el flujo completo de los documentos y escenarios extraordinarios (archivos corruptos, formatos inválidos, payloads pesados).
Para correr la suite completa de tests en un entorno Docker aislado:
```bash
make test

```
## Variables de Entorno

Configuración centralizada en `app/core/config.py` usando **pydantic-settings**.

| Variable | Requerida | Default | Descripción |
|----------|-----------|---------|-------------|
| `MONGO_URI` | **Sí** | — | URI de conexión a MongoDB |
| `MONGO_DATABASE_NAME` | No | `pdf_db` | Nombre de la base de datos |
| `MONGO_COLLECTION_NAME` | No | `pdfs` | Nombre de la colección |
| `APP_TITLE` | No | `Proyecto Convertidor - API Conversor PDF` | Título de la app |
| `APP_HOST` | No | `0.0.0.0` | Host de escucha de Uvicorn |
| `APP_PORT` | No | `8000` | Puerto de escucha de Uvicorn |
| `MAX_FILE_SIZE_MB` | No | `50` | Tamaño máximo de archivo (MB) |
| `ALLOWED_FILE_EXTENSION` | No | `.pdf` | Extensión de archivo permitida |


## Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/upload-pdf` | Subir PDF, extraer texto y guardar |
| `GET` | `/pdfs` | Listar todos los PDFs almacenados |
| `GET` | `/pdfs/{id}` | Obtener un PDF específico por ID |
| `PATCH` | `/pdfs/{id}` | Actualizar metadatos (filename) |
| `DELETE` | `/pdfs/{id}` | Eliminar un PDF de la base de datos |

Los errores de `POST /upload-pdf` responden con Problem Details (RFC 9457) en
`application/problem+json`.


## Arquitectura

Arquitectura en capas con núcleo de dominio y puertos/adaptadores. No se afirma una arquitectura Clean/Hexagonal completa; se documenta lo realmente implementado.

### Flujo

```
API
↓
Services (casos de uso)  ←  PDFRepositoryPort (puerto en app/services/ports.py)
↓                           ↗
Domain (entidad + excepciones puras)
↑
Repository (adaptador MongoDB) + Mappers (MongoDB ↔ Dominio / Dominio ↔ DTO)
↓
Infrastructure (FastAPI, Motor/MongoDB, configuración)
```

### Estructura del proyecto

```
pdf-extractext
├── app/
│   ├── main.py                  # Punto de entrada de la aplicación
│   ├── core/                    # Configuración y transversal
│   │   ├── config.py            # Configuración centralizada (pydantic-settings)
│   │   ├── logger.py            # Logging
│   │   └── middleware.py        # Middleware HTTP
│   ├── api/                     # Capa API (adaptador HTTP)
│   │   ├── health.py            # Router de health check
│   │   ├── dependencies.py      # Composition Root / inyección de dependencias
│   │   ├── mappers.py           # Dominio → DTO (PDFDocument → PDFDocumentResponse)
│   │   ├── upload_reader.py     # Lectura técnica del archivo en chunks
│   │   └── endpoints/
│   │       ├── upload.py        # Adapter HTTP de subida de PDFs
│   │       └── pdfs.py          # Endpoints CRUD de PDFs
│   ├── domain/                  # Núcleo de dominio (puro, sin FastAPI/MongoDB)
│   │   ├── pdf_document.py      # Entidad PDFDocument
│   │   └── exceptions.py        # Excepciones puras de dominio/aplicación
│   ├── services/                # Casos de uso / lógica de aplicación
│   │   ├── ports.py             # Puertos (PDFRepositoryPort) para inversión de dependencias
│   │   ├── pdf_service.py       # Casos de uso de documentos PDF
│   │   ├── checksum.py          # Cálculo de checksums SHA-256
│   │   └── upload_policy.py     # Reglas de validación del archivo subido
│   ├── repository/              # Adaptador de persistencia (MongoDB)
│   │   ├── database.py          # Conexión a MongoDB
│   │   ├── mappers.py           # MongoDB ↔ Dominio (mongo_to_domain / domain_to_mongo)
│   │   └── pdf_repository.py    # Operaciones CRUD contra MongoDB
│   ├── models/                  # DTOs/esquemas Pydantic de la API
│   │   └── pdf_models.py        # PDFDocumentResponse, PDFUpdateRequest
│   └── exceptions/              # Excepciones HTTP/RFC 9457
│       └── rfc9457.py           # Errores estandarizados Problem Details
├── infra/
│   ├── docker-compose.db.yml    # Contenedor aislado de MongoDB
│   ├── docker-compose.test.yml  # Override temporal para testing
│   ├── docker-compose.yml       # Contenedor principal de la API
│   └── Dockerfile               # Multi-stage build de la aplicación
├── tests/
│   ├── api/                     # Tests de endpoints
│   ├── audits/                  # Auditoría arquitectónica (AST)
│   ├── core/                    # Tests de configuración
│   ├── domain/                  # Tests de dominio
│   ├── exceptions/              # Tests de manejo de errores
│   ├── models/                  # Tests de esquemas Pydantic
│   ├── repository/              # Tests de conexión, mappers y CRUD
│   ├── services/                # Tests de lógica de aplicación
│   └── fixtures/                # Archivos PDF de prueba estáticos
├── .env.example                # Plantilla de variables de entorno
├── Makefile                    # Atajos para comandos de terminal
├── pyproject.toml              # Declaración de dependencias
└── uv.lock                     # Lockfile estricto de dependencias
```

## Metodologías Aplicadas

- **Test Driven Development (TDD)**
- **12-Factor App**
- **Clean Code**
- **Arquitectura en capas con núcleo de dominio y puertos/adaptadores**
- **Principios SOLID**, **KISS**, **DRY**, **YAGNI**


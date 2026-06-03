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
- **Arquitectura en capas** con separación de responsabilidades
- **Configuración centralizada** mediante variables de entorno

## Tecnologias

Python 3.12+ | FastAPI | Pydantic | PyMuPDF | Motor | MongoDB | Docker | Pytest

## Requisitos

| Componente | Versión |
|---|---|
| Docker | 20.10+ |
| Docker Compose | 2.0+ |

## Instalación y configuración

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd pdf-extractext

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Levantar los servicios (app + MongoDB)
make up

# 4. Correr los tests de forma aislada
make test

La API estará disponible en:
- **API:** http://localhost:8000
- **Documentación interactiva:** http://localhost:8000/docs

# Detener contenedores
make down

# Reconstruir la imagen (ej. al agregar nuevas dependencias)
make build

## Variables de Entorno

Configuración centralizada en `app/core/config.py` usando **pydantic-settings**.

| Variable | Requerida | Default | Descripción |
|----------|-----------|---------|-------------|
| `MONGO_URI` | **Sí** | — | URI de conexión a MongoDB |
| `MONGO_DATABASE_NAME` | No | `pdf_db` | Nombre de la base de datos |
| `MONGO_COLLECTION_NAME` | No | `pdfs` | Nombre de la colección |
| `APP_TITLE` | No | `Proyecto Convertidor - API Conversor PDF` | Título de la app |
| `APP_HOST` | No | `0.0.0.0` | Host del servidor |
| `APP_PORT` | No | `8000` | Puerto del servidor |
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

```

## Testing

```bash
# Ejecutar todos los tests
docker compose exec app pytest tests/ -v

# Tests específicos por módulo
docker compose exec app pytest tests/services/ -v
docker compose exec app pytest tests/api/ -v
docker compose exec app pytest tests/models/ -v
```

## Arquitectura

El proyecto sigue una arquitectura limpia con separación de responsabilidades:

```
app/
├── main.py                  # Punto de entrada de la aplicación
├── core/
│   └── config.py              # Configuración centralizada
├── api/
│   ├── health.py              # Router de health check
│   ├── dependencies.py        # Dependencias inyectables
│   └── endpoints/
│       ├── upload.py          # Endpoint de subida de PDFs
│       └── pdfs.py            # Endpoints CRUD de PDFs
├── models/
│   └── pdf_models.py          # Esquemas Pydantic
├── services/
│   ├── checksum.py            # Cálculo de checksums SHA-256
│   └── pdf_service.py         # Lógica de extracción de texto
├── repository/
│   ├── database.py            # Conexión a MongoDB
│   └── pdf_repository.py      # Operaciones CRUD
└── exceptions/
    └── rfc9457.py             # Manejo de errores estandarizado

tests/
├── api/                       # Tests de endpoints
├── core/                      # Tests de configuración
├── models/                    # Tests de esquemas Pydantic
├── repository/                # Tests de conexión y CRUD
├── services/                  # Tests de lógica de negocio
└── exceptions/                # Tests de manejo de errores
```

## Metodologías Aplicadas

- **Test Driven Development (TDD)**
- **12-Factor App** (Configuración en variables de entorno)
- **Clean Code** y **Clean Architecture**
- **Principios SOLID**, **KISS**, **DRY**, **YAGNI**

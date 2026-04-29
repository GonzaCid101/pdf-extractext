# PDF Extractext

**Integrantes**

- **Gonzalo Cid**
- **Manuel Andres Perez**
- **Juan Manuel De Los Rios**
- **Bruno Alcaraz**

---

## Descripción del Proyecto

API REST para extraer texto de archivos PDF y almacenarlos en MongoDB. Permite subir documentos, extraer su contenido textual, generar checksums SHA-256 para verificación de integridad de datos y gestionar los documentos almacenados mediante operaciones CRUD completas.

**Funcionalidades principales:**
- Procesamiento 100% en memoria
- Extracción de texto de archivos PDF usando PyMuPDF
- Generación de checksums SHA-256 para integridad de datos
- Almacenamiento en MongoDB con Motor (driver async)
- API REST con FastAPI y documentación automática Swagger UI
- Arquitectura en capas (API, Models, Services, Repository)

---

## Requerimientos del Sistema

### Software Necesario

| Componente | Versión | Descripción |
|------------|---------|-------------|
| Docker | 20.10+ | Containerización de servicios |
| Docker Compose | 2.0+ | Orquestación de contenedores |
| Git | 2.30+ | Control de versiones |
| Python | 3.12+ | Lenguaje de programación (incluido en Docker) |
---

## Instalación y Configuración

### Paso 1: Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd pdf-extractext
```

### Paso 2: Configurar Variables de Entorno

**Obligatorio:** Crear el archivo `.env` en la raíz del proyecto basándose en `.env.example`:

```bash
cp .env.example .env
```

**Configurar el archivo `.env`:**

Editar el archivo `.env` y asegurarse de que contenga:

```
MONGO_URI=mongodb://db:27017/conversor_pdf
```

### Paso 3: Verificar Estructura del Proyecto

La estructura del proyecto debe ser:

```
pdf-extractext/
├── .env                    # Archivo de variables de entorno (creado en Paso 2)
├── .env.example            # Template de variables
├── docker-compose.yml      # Configuración de servicios
├── Dockerfile              # Imagen de la aplicación
├── pyproject.toml          # Dependencias y configuración
├── README.md               # Este archivo
└── app/                    # Código fuente
    ├── main.py
    ├── api/
    ├── models/
    ├── services/
    └── repository/
```

---

## Ejecución de la Aplicación

### Paso 1: Levantar los Servicios

```bash
docker compose up --build -d
```
### Paso 2: Verificar que los Servicios Están Corriendo

```bash
docker compose ps
```
### Paso 3: Acceder a la Documentación de la API

Abrir el navegador en:

```
http://localhost:8000/docs
```

### Paso 4: Detener los Servicios

```bash
docker compose down
```

```bash
docker compose down -v
```

---

## Endpoints de la API

### Resumen de Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Health check - Verificar estado de la API |
| POST | `/upload-pdf` | Subir PDF, extraer texto y guardar en MongoDB |
| GET | `/pdfs` | Listar todos los PDFs almacenados |
| GET | `/pdfs/{id}` | Obtener un PDF específico por su ID |
| PATCH | `/pdfs/{id}` | Actualizar metadatos (filename) de un PDF |
| DELETE | `/pdfs/{id}` | Eliminar físicamente un PDF de la base de datos |

## Testing

### Ejecutar Todos los Tests

```bash
docker compose exec app pytest tests/ -v
```

**Qué se prueba:**
- Extracción de texto de PDFs
- Generación de checksums
- Validaciones de modelos Pydantic
- Endpoints de la API
- Conexión a MongoDB

### Ejecutar Tests Específicos

**Tests de servicios:**
```bash
docker compose exec app pytest tests/services/ -v
```

**Tests de API:**
```bash
docker compose exec app pytest tests/api/ -v
```

**Tests de modelos:**
```bash
docker compose exec app pytest tests/models/ -v
```

### Cobertura de Tests

El proyecto incluye tests para:
- ✅ Procesamiento de PDFs válidos e inválidos
- ✅ Generación y verificación de checksums
- ✅ Validaciones de modelos de datos
- ✅ Operaciones CRUD en MongoDB
- ✅ Endpoints REST con diferentes escenarios

---

## Arquitectura

### Separación en Capas

El proyecto sigue una arquitectura limpia con separación de responsabilidades:

```
app/
├── api/                    # Capa de Presentación
│   ├── endpoints/          # Routers de FastAPI
│   │   ├── health.py       # Health check
│   │   ├── upload.py       # Subida de PDFs
│   │   └── pdfs.py         # CRUD de PDFs
│   └── health.py           # Router de health check
├── models/                 # Capa de Dominio
│   └── pdf_models.py       # Esquemas Pydantic
├── services/               # Capa de Lógica de Negocio
│   ├── checksum.py         # Cálculo de checksums
│   └── pdf_service.py      # Extracción de texto
└── repository/             # Capa de Datos
    ├── database.py         # Conexión a MongoDB
    └── pdf_repository.py   # Operaciones CRUD
```

### Características de la Arquitectura

- **API**: Endpoints FastAPI, routing, validación de requests
- **Models**: Esquemas Pydantic para request/response/validación
- **Services**: Lógica de negocio pura, sin dependencias de framework ni BD
- **Repository**: Acceso a datos MongoDB, operaciones asíncronas con Motor

### Principios Aplicados

- **Procesamiento 100% en memoria**
- **Configuración en variables de entorno**
- **Separación de responsabilidades**
- **Inyección de dependencias**

---

## Metodologías y Principios

### Metodologías

- **TDD (Test Driven Development)**
- **12 Factor App**
- **Clean Code**
- **Clean Architecture**

### Principios de Programación

- **KISS**
- **DRY**
- **YAGNI**
- **SOLID**:

---

## Tecnologías Utilizadas
- Python
- FastAPI
- Pydantic
- PyMuPDF
- Motor
- MongoDB
- Pytest
- Docker
- Uvicorn
- Hatchling


# pdf-extractext

Extraer texto de un pdf que es proporcionado por el usuario. Después se hace un resumen gracias al modelo de IA.

## Tecnologias:
- Python 3.12+
- FastAPI
- PyMuPDF (fitz)
- MongoDB (Motor)
- Pytest
- Docker
- Modelo de IA (a definir)

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/upload-pdf` | Subir PDF y extraer texto |

## Arquitectura

Tres capas separadas:
- **API**: Endpoints FastAPI (`app/api/`)
- **Services**: Lógica de negocio (`app/services/`)
- **Repository**: Acceso a MongoDB (`app/repository/`)

## Desarrollo

Levantar servicios:
```bash
docker compose up --build -d
```

Ejecutar tests:
```bash
docker compose exec app pytest tests/ -v
```

## Metodologias:

- TDD
- Proyecto dirigido en GitHub
- Los 6 primeros principios de 12 factor APP
- Clean Code

## Principios de Programacion:

- KISS
- DRY
- YAGNI
- SOLID

FROM python:3.12-slim

# Varibles de entorno para el build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear grupo y usuario sin privilegios
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Instalar uv
RUN pip install uv

# Establecer directorio de trabajo
WORKDIR /app

# Copiar solo los archivos necesarios para instalar dependencias
COPY pyproject.toml README.md ./

# Instalar dependencias en el sistema
RUN uv pip install --system -e .

# Copiar el codigo de la aplicacion
COPY app/ ./app/

# Asignar permisos al usuario sin privilegios
RUN chown -R appuser:appgroup /app

# Cambiar al usuario no privilegiado
USER appuser

# Exponer el puerto (Uvicorn lee de $PORT)
EXPOSE ${PORT}

# Ejecutar Uvicorn con workers parametrizados
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS}

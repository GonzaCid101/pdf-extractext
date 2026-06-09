# -- Etapa Builder --
FROM python:3.14.0-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install uv

# Archivos de configuracion y lock
COPY pyproject.toml uv.lock README.md ./

# Generar entorno virtual siguiendo lock
RUN uv sync --frozen

COPY app/ ./app/

# -- Etapa Runner --
FROM python:3.14.0-slim AS runner

# Paquete de zonas horarias
ENV TZ="America/Argentina/Mendoza"
RUN apt-get update && apt-get install -y tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Crear grupo y usuario sin privilegios
RUN groupadd -r appgroup && useradd -m -r -g appgroup appuser

WORKDIR /app

# Obtener dependencias y codigo del builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app

# Asignar permisos
RUN chown -R appuser:appgroup /app

USER appuser

# Exponer el puerto
EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH"
# Ejecutar Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]



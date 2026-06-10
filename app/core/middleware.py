"""Middleware de trazabilidad y registro de peticiones HTTP."""

import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = uuid4().hex
        start_time = time.perf_counter()

        logger.info(
            f"Inicia petición: {request.method} {request.url.path} - ID: {request_id}"
        )

        response = await call_next(request)

        duration = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Termina petición: {response.status_code} en {duration:.2f}ms - ID: {request_id}"
        )

        response.headers["X-Request-ID"] = request_id
        return response

"""Configuración centralizada de logging compatibile con 12-Factor App."""

import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_BUENOS_AIRES = ZoneInfo("America/Argentina/Buenos_Aires")


class BuenosAiresFormatter(logging.Formatter):
    """Formateador que convierte timestamps a zona horaria de Buenos Aires."""

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=TZ_BUENOS_AIRES)
        return dt.strftime(datefmt or self.default_time_format)


def setup_logging() -> None:
    """Configura el logging raíz con salida a stdout y zona horaria de Argentina."""
    log_formatter = BuenosAiresFormatter(
        "[%(asctime)s] | [%(levelname)s] | [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not root_logger.hasHandlers():
        root_logger.addHandler(stream_handler)

    uvicorn_loggers = ("uvicorn", "uvicorn.error", "uvicorn.access")
    for logger_name in uvicorn_loggers:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.addHandler(stream_handler)
        uvicorn_logger.setLevel(logging.INFO)
        uvicorn_logger.propagate = False

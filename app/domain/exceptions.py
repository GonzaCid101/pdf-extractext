# FASE GREEN: Implementación mínima para pasar el test
"""Excepciones puras de dominio/aplicación.

Regla de Oro: cero acoplamiento con la capa web (fastapi/starlette).
"""


class DuplicatePDFError(Exception):
    """Se intentó registrar un PDF que ya existe en el sistema."""


class PDFNotFoundError(Exception):
    """El PDF solicitado no existe en el sistema."""

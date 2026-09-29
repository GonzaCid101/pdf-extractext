# FASE RED: Este test fallará inicialmente
"""Tests para las excepciones de dominio (Sub-issue #40)."""

import pytest

from app.domain.exceptions import DuplicatePDFError, PDFNotFoundError


class TestDuplicatePDFError:
    def test_hereda_de_exception(self):
        assert issubclass(DuplicatePDFError, Exception)

    def test_mensaje_personalizado(self):
        error = DuplicatePDFError("checksum duplicado")
        assert str(error) == "checksum duplicado"

    def test_puede_lanzarse_y_capturarse(self):
        with pytest.raises(DuplicatePDFError):
            raise DuplicatePDFError("ya existe")


class TestPDFNotFoundError:
    def test_hereda_de_exception(self):
        assert issubclass(PDFNotFoundError, Exception)

    def test_mensaje_personalizado(self):
        error = PDFNotFoundError("id=123 no encontrado")
        assert str(error) == "id=123 no encontrado"

    def test_puede_lanzarse_y_capturarse(self):
        with pytest.raises(PDFNotFoundError):
            raise PDFNotFoundError("no existe")


def test_sin_acoplamiento_web():
    """Regla de Oro: ninguna dependencia de fastapi/starlette."""
    import app.domain.exceptions as module

    assert "fastapi" not in module.__dict__
    assert "starlette" not in module.__dict__

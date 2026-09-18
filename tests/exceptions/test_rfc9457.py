"""Tests para excepciones basadas en RFC 9457."""

import inspect

import pytest
from http import HTTPStatus as status

from app.exceptions.rfc9457 import RFC9457Exception, DuplicatePDFException


# FASE RED: Este test fallará inicialmente
def test_rfc9457_sin_dependencias_web():
    """Regla de Oro: el módulo no puede importar fastapi ni starlette."""
    import app.exceptions.rfc9457 as module

    source = inspect.getsource(module)
    assert "fastapi" not in source
    assert "starlette" not in source


class TestRFC9457Exception:
    def test_base_fields(self):
        exc = RFC9457Exception(
            type_="about:blank",
            title="Error de validación",
            status=status.BAD_REQUEST,
            detail="El campo 'email' es requerido",
            instance="/upload-pdf",
        )
        assert exc.type == "about:blank"
        assert exc.title == "Error de validación"
        assert exc.status == 400
        assert exc.detail == "El campo 'email' es requerido"
        assert exc.instance == "/upload-pdf"

    def test_to_dict_returns_all_fields(self):
        exc = RFC9457Exception(
            type_="about:blank",
            title="Error de validación",
            status=status.BAD_REQUEST,
            detail="El campo 'email' es requerido",
            instance="/upload-pdf",
        )
        result = exc.to_dict()
        assert result == {
            "type": "about:blank",
            "title": "Error de validación",
            "status": 400,
            "detail": "El campo 'email' es requerido",
            "instance": "/upload-pdf",
        }

    def test_custom_fields_in_dict(self):
        exc = RFC9457Exception(
            type_="about:blank",
            title="Error de validación",
            status=status.BAD_REQUEST,
            detail="El campo 'email' es requerido",
            instance="/upload-pdf",
            custom_field="valor personalizado",
        )
        result = exc.to_dict()
        assert result["custom_field"] == "valor personalizado"


class TestDuplicatePDFException:
    def test_default_fields(self):
        exc = DuplicatePDFException()
        assert exc.type == "urn:pdf-extractext:errors:duplicate-pdf"
        assert exc.title == "Documento PDF duplicado"
        assert exc.status == status.CONFLICT
        assert exc.detail == "El documento ya existe en el sistema"
        assert exc.instance == "/upload-pdf"

    def test_custom_detail(self):
        exc = DuplicatePDFException(detail="PDF ya registrado")
        assert exc.detail == "PDF ya registrado"

    def test_is_rfc9457_exception(self):
        """Verifica que hereda de RFC9457Exception"""
        exc = DuplicatePDFException()
        assert isinstance(exc, RFC9457Exception)

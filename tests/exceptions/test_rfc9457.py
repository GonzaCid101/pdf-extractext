"""Tests para excepciones basadas en RFC 9457."""

import inspect

import pytest
from http import HTTPStatus as status

from app.exceptions.rfc9457 import (
    RFC9457Exception,
    DuplicatePDFException,
    EmptyFileException,
    EmptyUpdateException,
    FilenameTooLongException,
    FileTooLargeException,
    InvalidFileExtensionException,
    InvalidPDFContentException,
    PDFNotFoundException,
)


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


_UPLOAD_PROBLEMS = [
    (
        InvalidFileExtensionException,
        "urn:pdf-extractext:errors:invalid-file-extension",
        "Extensión de archivo no permitida",
        status.UNSUPPORTED_MEDIA_TYPE,
    ),
    (
        FileTooLargeException,
        "urn:pdf-extractext:errors:file-too-large",
        "Archivo demasiado grande",
        status.REQUEST_ENTITY_TOO_LARGE,
    ),
    (
        EmptyFileException,
        "urn:pdf-extractext:errors:empty-file",
        "Archivo vacío",
        status.BAD_REQUEST,
    ),
    (
        InvalidPDFContentException,
        "urn:pdf-extractext:errors:invalid-pdf-content",
        "Contenido PDF inválido",
        status.UNSUPPORTED_MEDIA_TYPE,
    ),
    (
        FilenameTooLongException,
        "urn:pdf-extractext:errors:filename-too-long",
        "Nombre de archivo demasiado largo",
        status.UNSUPPORTED_MEDIA_TYPE,
    ),
]


@pytest.mark.parametrize(
    "problem_class, expected_type, expected_title, expected_status",
    _UPLOAD_PROBLEMS,
    ids=[case[0].__name__ for case in _UPLOAD_PROBLEMS],
)
def test_problemas_de_upload_cumplen_rfc9457(
    problem_class, expected_type, expected_title, expected_status
):
    exc = problem_class(detail="detalle del problema")

    assert isinstance(exc, RFC9457Exception)
    assert exc.type == expected_type
    assert exc.title == expected_title
    assert exc.status == expected_status
    assert exc.detail == "detalle del problema"
    assert exc.instance == "/upload-pdf"


class TestPDFNotFoundException:
    # FASE RED: Este test fallará inicialmente
    def test_default_fields(self):
        exc = PDFNotFoundException(instance="/pdfs/65797e91c185b4c7c5a93a99")

        assert exc.type == "urn:pdf-extractext:errors:pdf-not-found"
        assert exc.title == "PDF no encontrado"
        assert exc.status == status.NOT_FOUND
        assert exc.detail == "PDF no encontrado"
        assert exc.instance == "/pdfs/65797e91c185b4c7c5a93a99"

    def test_custom_detail(self):
        exc = PDFNotFoundException(
            instance="/pdfs/1",
            detail="PDF con id '1' no encontrado",
        )

        assert exc.detail == "PDF con id '1' no encontrado"


class TestEmptyUpdateException:
    # FASE RED: Este test fallará inicialmente
    def test_default_fields(self):
        exc = EmptyUpdateException(instance="/pdfs/1")

        assert exc.type == "urn:pdf-extractext:errors:empty-update"
        assert exc.title == "Sin campos para actualizar"
        assert exc.status == status.BAD_REQUEST
        assert exc.detail == "No se proporcionó ningún campo para actualizar"
        assert exc.instance == "/pdfs/1"

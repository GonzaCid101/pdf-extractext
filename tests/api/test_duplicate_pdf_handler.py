# FASE RED: Este test fallará inicialmente
"""Tests unitarios del exception handler global para DuplicatePDFError
(Sub-issue #43). No requieren MongoDB: invocan el handler directamente.
"""

import json

from starlette.requests import Request

from app.domain.exceptions import DuplicatePDFError
from app.main import duplicate_pdf_error_handler


def _make_request(path: str = "/upload-pdf") -> Request:
    return Request({"type": "http", "method": "POST", "path": path, "headers": []})


class TestDuplicatePDFErrorHandler:
    async def test_status_code_409(self):
        response = await duplicate_pdf_error_handler(
            _make_request(), DuplicatePDFError("El documento ya existe en el sistema")
        )
        assert response.status_code == 409

    async def test_content_type_problem_json(self):
        response = await duplicate_pdf_error_handler(
            _make_request(), DuplicatePDFError("El documento ya existe en el sistema")
        )
        assert "application/problem+json" in response.media_type

    async def test_body_estructura_rfc9457(self):
        response = await duplicate_pdf_error_handler(
            _make_request(), DuplicatePDFError("El documento ya existe en el sistema")
        )
        problem = json.loads(response.body)
        assert problem["type"] == "urn:pdf-extractext:errors:duplicate-pdf"
        assert problem["title"] == "Documento PDF duplicado"
        assert problem["status"] == 409
        assert problem["detail"] == "El documento ya existe en el sistema"
        assert problem["instance"] == "/upload-pdf"

    async def test_handler_registrado_en_app(self):
        from app.main import app

        assert DuplicatePDFError in app.exception_handlers, (
            "DuplicatePDFError debe tener un exception handler global registrado"
        )

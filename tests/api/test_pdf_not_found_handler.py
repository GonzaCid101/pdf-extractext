# FASE RED: Este test fallará inicialmente
"""Tests unitarios del handler global PDFNotFoundError → RFC 9457."""

import json

from starlette.requests import Request

from app.domain.exceptions import PDFNotFoundError
from app.main import app, pdf_not_found_error_handler


def _make_request(path: str = "/pdfs/65797e91c185b4c7c5a93a99") -> Request:
    return Request({"type": "http", "method": "GET", "path": path, "headers": []})


class TestPDFNotFoundErrorHandler:
    async def test_status_code_404(self):
        response = await pdf_not_found_error_handler(
            _make_request(), PDFNotFoundError("PDF con id 'x' no encontrado")
        )
        assert response.status_code == 404

    async def test_content_type_problem_json(self):
        response = await pdf_not_found_error_handler(
            _make_request(), PDFNotFoundError("PDF no encontrado")
        )
        assert "application/problem+json" in response.media_type

    async def test_body_estructura_rfc9457(self):
        response = await pdf_not_found_error_handler(
            _make_request(), PDFNotFoundError("PDF no encontrado")
        )
        problem = json.loads(response.body)
        assert problem["type"] == "urn:pdf-extractext:errors:pdf-not-found"
        assert problem["status"] == 404
        assert problem["instance"].startswith("/pdfs/")

    def test_handler_registrado_en_app(self):
        assert PDFNotFoundError in app.exception_handlers

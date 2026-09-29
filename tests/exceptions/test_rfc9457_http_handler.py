"""Issue #70: verificación a nivel HTTP del handler RFC 9457 de main.py.

# FASE RED: Este test falla si el handler no serializa con el media type
# application/problem+json o si la estructura de la respuesta está incompleta.
"""


class TestRFC9457HttpHandler:
    """El handler rfc9457_exception_handler debe devolver Problem Details."""

    async def test_handler_returns_problem_json_media_type(self, async_client):
        response = await async_client.get("/pdfs/abc")

        assert response.headers["content-type"].startswith(
            "application/problem+json"
        )

    async def test_handler_returns_full_problem_structure(self, async_client):
        response = await async_client.get("/pdfs/abc")

        assert response.status_code == 400

        problem = response.json()
        assert problem["type"] == "urn:pdf-extractext:errors:invalid-object-id"
        assert problem["title"] == "ObjectId malformado"
        assert problem["status"] == 400
        assert problem["instance"] == "/pdfs/abc"
        assert "detail" in problem

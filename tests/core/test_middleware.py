"""Tests para middleware de trazabilidad."""

from fastapi.testclient import TestClient

from app.main import app


class TestTracingMiddleware:
    def test_request_returns_x_request_id_header(self):
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        assert "x-request-id" in response.headers

        request_id = response.headers["x-request-id"]
        assert len(request_id) == 32

    def test_request_id_is_unique(self):
        client = TestClient(app)

        response1 = client.get("/")
        response2 = client.get("/")

        assert response1.headers["x-request-id"] != response2.headers["x-request-id"]

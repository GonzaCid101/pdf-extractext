from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthcheck():
    """Verifica que el endpoint de health check responde correctamente."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "API Conversor PDF funcionando"}

"""Tests para aplicación principal."""


class TestHealthCheck:
    """Tests para endpoint de health check."""

    def test_returns_200_with_message(self, test_client):
        """Retorna 200 con mensaje."""
        response = test_client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "PDF Extractext API funcionando"}

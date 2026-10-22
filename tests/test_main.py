"""Tests para aplicación principal."""

from unittest.mock import patch

from app import main
from app.core.config import settings


class TestHealthCheck:
    """Tests para endpoint de health check."""

    def test_returns_200_with_message(self, test_client):
        """Retorna 200 con mensaje."""
        response = test_client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "PDF Extractext API funcionando"}


class TestMainRun:
    def test_run_usa_settings_para_host_y_port(self):
        with patch.object(main.uvicorn, "run") as mock_run:
            main.run()
            mock_run.assert_called_once_with(
                "app.main:app",
                host=settings.APP_HOST,
                port=settings.APP_PORT,
                workers=4,
            )

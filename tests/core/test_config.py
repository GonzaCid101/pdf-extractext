"""Tests para configuración de la aplicación."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.config import Settings


class SettingsNoEnvFile(BaseSettings):

    model_config = SettingsConfigDict(env_file=None)

    MONGO_URI: str
    MONGO_DATABASE_NAME: str = "pdf_db"
    MONGO_COLLECTION_NAME: str = "pdfs"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_EXTENSION: str = ".pdf"


class TestSettings:
    def test_valores_por_defecto(self):
        # Proveemos MONGO_URI y verificamos los demás valores por defecto
        env_vars = {"MONGO_URI": "mongodb://localhost:27017/test"}
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            assert settings.MONGO_DATABASE_NAME == "pdf_db"
            assert settings.MONGO_COLLECTION_NAME == "pdfs"
            assert settings.APP_PORT == 8000
            assert settings.APP_HOST == "0.0.0.0"
            assert settings.MAX_FILE_SIZE_MB == 50
            assert settings.ALLOWED_FILE_EXTENSION == ".pdf"

    def test_variables_entorno_superpuestas(self):
        env_vars = {
            "MONGO_URI": "mongodb://localhost:27017/test",
            "MONGO_DATABASE_NAME": "test_db",
            "MONGO_COLLECTION_NAME": "test_pdfs",
            "APP_PORT": "9000",
            "APP_HOST": "127.0.0.1",
            "MAX_FILE_SIZE_MB": "100",
            "ALLOWED_FILE_EXTENSION": ".doc",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            assert settings.MONGO_DATABASE_NAME == "test_db"
            assert settings.MONGO_COLLECTION_NAME == "test_pdfs"
            assert settings.APP_PORT == 9000
            assert settings.APP_HOST == "127.0.0.1"
            assert settings.MAX_FILE_SIZE_MB == 100
            assert settings.ALLOWED_FILE_EXTENSION == ".doc"

    def test_mongo_uri_requerida(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError):
                SettingsNoEnvFile()

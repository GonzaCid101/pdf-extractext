"""Configuración centralizada de la aplicación usando pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # MongoDB
    MONGO_URI: str
    MONGO_DATABASE_NAME: str = "pdf_db"
    MONGO_COLLECTION_NAME: str = "pdfs"

    # Application Server
    APP_TITLE: str = "Proyecto Convertidor - API Conversor PDF"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Upload Limits
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_EXTENSION: str = ".pdf"


settings = Settings()

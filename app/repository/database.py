"""Gestión de conexiones asíncronas a MongoDB usando Motor."""

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient


class MongoManager:
    """Gestiona conexiones asíncronas a MongoDB."""

    def __init__(self) -> None:
        self._mongo_uri: str = os.environ.get("MONGO_URI", "")
        self._client: Optional[AsyncIOMotorClient] = None

    def get_client(self) -> AsyncIOMotorClient:
        """Retorna el cliente de MongoDB (inicialización lazy)."""
        if self._client is None:
            self._client = AsyncIOMotorClient(self._mongo_uri)
        return self._client

    async def close(self) -> None:
        """Cierra la conexión a MongoDB."""
        if self._client is not None:
            self._client.close()
            self._client = None


_db_manager = MongoManager()


async def get_database():
    """Provee el cliente de MongoDB para inyección de dependencias de FastAPI."""
    yield _db_manager.get_client()

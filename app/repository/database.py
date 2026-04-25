"""Conexión asíncrona a MongoDB."""

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient


class MongoManager:
    def __init__(self) -> None:
        self._mongo_uri: str = os.environ.get("MONGO_URI", "")
        self._client: Optional[AsyncIOMotorClient] = None

    def get_client(self) -> AsyncIOMotorClient:
        """Retorna cliente MongoDB (lazy init)."""
        if self._client is None:
            self._client = AsyncIOMotorClient(self._mongo_uri)
        return self._client

    async def close(self) -> None:
        """Cierra conexión MongoDB."""
        if self._client is not None:
            self._client.close()
            self._client = None


_db_manager = MongoManager()


async def get_database():
    """Provee cliente MongoDB para inyección de dependencias."""
    yield _db_manager.get_client()

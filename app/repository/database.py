"""Conexión asíncrona a MongoDB."""

import os
from typing import AsyncGenerator, Optional

from motor.motor_asyncio import AsyncIOMotorClient


class MongoManager:
    """Gestor de conexiones MongoDB con lazy initialization."""

    def __init__(self) -> None:
        self._mongo_uri: str = os.environ.get("MONGO_URI", "")
        self._client: Optional[AsyncIOMotorClient] = None

    def get_client(self) -> AsyncIOMotorClient:
        if self._client is None:
            self._client = AsyncIOMotorClient(self._mongo_uri)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None


_db_manager = MongoManager()


async def get_database() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Provee cliente MongoDB fresh para cada request.

    Crea un nuevo cliente en cada llamada para evitar problemas
    de event loop compartido entre tests.
    """
    mongo_uri = os.environ.get("MONGO_URI", "")
    client = AsyncIOMotorClient(mongo_uri)
    try:
        yield client
    finally:
        client.close()

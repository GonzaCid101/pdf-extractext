"""Database connection management module.

Provides async MongoDB connectivity using Motor driver with
connection lifecycle management.
"""

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient


class MongoManager:
    """Manages MongoDB async client connections.

    Handles connection lifecycle and provides access to Motor client
    for database operations. Reads MONGO_URI from environment.
    """

    def __init__(self) -> None:
        """Initialize MongoDB manager without creating client."""
        self._mongo_uri: str = os.environ.get("MONGO_URI", "")
        self._client: Optional[AsyncIOMotorClient] = None

    def get_client(self) -> AsyncIOMotorClient:
        """Return the Motor async client instance (lazy initialization).

        Returns:
            AsyncIOMotorClient: Configured async MongoDB client.
        """
        if self._client is None:
            self._client = AsyncIOMotorClient(self._mongo_uri)
        return self._client

    async def close(self) -> None:
        """Close the MongoDB connection gracefully."""
        if self._client is not None:
            self._client.close()
            self._client = None


_db_manager = MongoManager()


async def get_database():
    """Yield MongoDB client for FastAPI dependency injection.

    Yields:
        AsyncIOMotorClient: MongoDB client instance.
    """
    yield _db_manager.get_client()

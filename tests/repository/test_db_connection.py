"""Tests para conexión a base de datos."""

import pytest

from app.repository.database import MongoManager, get_database


class TestGetDatabase:
    """Tests para get_database."""

    @pytest.mark.asyncio
    async def test_returns_valid_client(self):
        """Retorna cliente válido."""
        db_gen = get_database()
        db = await anext(db_gen)

        assert db is not None
        assert hasattr(db, "admin")

        await db_gen.aclose()


class TestMongoManager:
    """Tests para MongoManager."""

    @pytest.mark.asyncio
    async def test_ping_returns_ok(self):
        """Ping retorna ok."""
        manager = MongoManager()
        client = manager.get_client()

        result = await client.admin.command("ping")

        assert result == {"ok": 1.0}

        await manager.close()

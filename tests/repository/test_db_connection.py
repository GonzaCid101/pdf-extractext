import pytest

from app.repository.database import MongoManager, get_database


@pytest.mark.asyncio
async def test_get_database_returns_client():
    """Verifica que get_database() retorna un cliente válido."""
    db_gen = get_database()
    db = await anext(db_gen)
    assert db is not None
    assert hasattr(db, "admin")
    await db_gen.aclose()


@pytest.mark.asyncio
async def test_mongo_connection_ping():
    """Verifica que MongoDB responde al comando ping."""
    mongo_manager = MongoManager()
    client = mongo_manager.get_client()

    result = await client.admin.command("ping")

    assert result == {"ok": 1.0}

    await mongo_manager.close()

"""Tests for MongoDB connection repository.

This module tests the database connection functionality
using Motor as the async MongoDB driver.
"""

import pytest

from app.repository.database import MongoManager, get_database


@pytest.mark.asyncio
async def test_get_database_returns_client():
    """Test that get_database() yields valid database client for dependency injection."""
    db_gen = get_database()
    db = await anext(db_gen)
    assert db is not None
    assert hasattr(db, "admin")
    await db_gen.aclose()


@pytest.mark.asyncio
async def test_mongo_connection_ping():
    """Test that MongoDB connection responds to ping command.

    Verifies the database is reachable by executing a ping command
    and checking the response is {'ok': 1.0}.
    """
    mongo_manager = MongoManager()
    client = mongo_manager.get_client()

    result = await client.admin.command("ping")

    assert result == {"ok": 1.0}

    await mongo_manager.close()

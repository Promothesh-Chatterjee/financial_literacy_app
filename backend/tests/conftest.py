import os
import tempfile
import asyncio
import shutil
import pytest
import pytest_asyncio

# Set env vars before importing app so pydantic Settings picks them up
TEST_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.db"))
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{TEST_DB}")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALLOW_DEV_INIT", "true")
os.environ.setdefault("MARKET_WORKER_SECRET", "test-secret")

from app.main import app
from app.db import engine, Base
import sqlalchemy


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def prepare_database(event_loop):
    # remove existing test db
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass

    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    event_loop.run_until_complete(_create())
    yield
    # teardown
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass


@pytest_asyncio.fixture
async def async_client():
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

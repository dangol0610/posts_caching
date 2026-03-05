import os

os.environ["TESTING"] = "True"

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.main import app
from src.settings.settings import settings
from src.utils.database import Base, get_session
from src.utils.redis import get_redis_client


@pytest.fixture(scope="function")
async def db_engine():
    """Создаёт тестовую БД."""
    engine = create_async_engine(settings.database_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine: AsyncEngine):
    """Создаёт сессию БД для теста."""
    async_session = async_sessionmaker(bind=db_engine, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def redis():
    """Создаёт Redis клиент для теста."""
    client = Redis.from_url(settings.redis_url)

    yield client

    await client.flushdb()  # Очищаем кэш после теста
    await client.close()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession, redis: Redis):
    """Создаёт HTTP клиент для тестов API."""

    # Переопределяем зависимости
    async def override_get_session():
        yield db_session

    async def override_get_redis():
        yield redis

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_redis_client] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

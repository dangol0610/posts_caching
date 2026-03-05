from typing import AsyncGenerator

from redis.asyncio import Redis

from src.settings.settings import settings

redis_client: Redis = Redis.from_url(settings.redis_url)


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    Получение соединения с Redis
    """
    yield redis_client

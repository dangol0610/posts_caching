from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.repository import PostsRepository
from src.app.services import PostsService
from src.utils.database import get_session
from src.utils.redis import get_redis_client

SessionDependency = Annotated[AsyncSession, Depends(get_session)]
RedisDependency = Annotated[Redis, Depends(get_redis_client)]


def get_repository(session: SessionDependency) -> PostsRepository:
    """Создание repository."""
    return PostsRepository(session)


RepositoryDependency = Annotated[PostsRepository, Depends(get_repository)]


def get_service(
    repository: RepositoryDependency,
    redis: RedisDependency,
) -> PostsService:
    """Создание service."""
    return PostsService(repository, redis)


ServiceDependency = Annotated[PostsService, Depends(get_service)]

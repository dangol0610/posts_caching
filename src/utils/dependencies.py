from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.repository import PostsRepository
from src.app.services import PostsService
from src.utils.database import get_session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def get_repository(session: SessionDependency) -> PostsRepository:
    """Создание repository."""
    return PostsRepository(session)


RepositoryDependency = Annotated[PostsRepository, Depends(get_repository)]


def get_service(repository: RepositoryDependency) -> PostsService:
    """Создание service."""
    return PostsService(repository)


ServiceDependency = Annotated[PostsService, Depends(get_service)]

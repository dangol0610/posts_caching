from sqlalchemy.ext.asyncio import AsyncSession


class PostsRepository:
    """Repository для работы с постами."""

    def __init__(self, session: AsyncSession):
        self.session = session

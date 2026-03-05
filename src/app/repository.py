from loguru import logger
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Post
from src.app.schemas import CreatePostDTO, UpdatePostDTO


class PostsRepository:
    """Repository для работы с постами."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(self, post: CreatePostDTO) -> Post:
        """Создание поста."""
        try:
            post_data = post.model_dump()
            stmt = insert(Post).values(post_data).returning(Post)
            res = await self.session.execute(stmt)
            logger.info("Post created successfully")
            await self.session.commit()
            return res.scalar_one()
        except SQLAlchemyError:
            logger.exception("Failed to create post")
            await self.session.rollback()
            raise

    async def get_by_id(self, post_id: int) -> Post | None:
        """Получение поста по id."""
        try:
            stmt = select(Post).where(Post.id == post_id)
            res = await self.session.execute(stmt)
            logger.info(f"Got post with id {post_id}")
            return res.scalar_one_or_none()
        except SQLAlchemyError:
            logger.exception(f"Failed to get post with id {post_id}")
            raise

    async def update_post(self, post_id: int, post: UpdatePostDTO) -> Post | None:
        """Обновление поста."""
        try:
            stmt = select(Post).where(Post.id == post_id)
            res = await self.session.execute(stmt)
            post_to_update = res.scalar_one_or_none()
            if not post_to_update:
                logger.info(f"Post with id {post_id} not found")
                return None
            post_data = post.model_dump(exclude_unset=True)
            stmt = (
                update(Post).where(Post.id == post_id).values(post_data).returning(Post)
            )
            res = await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"Updated post with id {post_id}")
            return res.scalar_one()
        except SQLAlchemyError:
            logger.exception(f"Failed to update post with id {post_id}")
            await self.session.rollback()
            raise

    async def delete_post(self, post_id: int) -> Post | None:
        """Удаление поста."""
        try:
            stmt = select(Post).where(Post.id == post_id)
            res = await self.session.execute(stmt)
            post_to_delete = res.scalar_one_or_none()
            if not post_to_delete:
                logger.info(f"Post with id {post_id} not found")
                return None
            stmt = delete(Post).where(Post.id == post_id)
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"Deleted post with id {post_id}")
            return post_to_delete
        except SQLAlchemyError:
            logger.exception(f"Failed to delete post with id {post_id}")
            await self.session.rollback()
            raise

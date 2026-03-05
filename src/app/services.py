from loguru import logger
from redis.asyncio import Redis, RedisError
from sqlalchemy.exc import SQLAlchemyError

from src.app.repository import PostsRepository
from src.app.schemas import CreatePostDTO, ReturnPostDTO, UpdatePostDTO
from src.utils.exceptions import CacheError, DatabaseError, PostNotFoundError


class PostsService:
    """Service для работы с постами."""

    def __init__(self, repository: PostsRepository, redis: Redis):
        self.repository = repository
        self.redis = redis

    async def create_post(self, post: CreatePostDTO) -> ReturnPostDTO:
        """Создание поста."""
        try:
            post_from_db = await self.repository.create_post(post)
            logger.info(f"Post created with id: {post_from_db.id}")
            return ReturnPostDTO.model_validate(post_from_db)
        except SQLAlchemyError:
            logger.exception("Failed to create post")
            raise DatabaseError

    async def get_post_by_id(self, post_id: int) -> ReturnPostDTO:
        """Получение поста по id. Если пост есть в кеше, возвращает его из кеша, иначе из БД и сохраняет в кеш."""
        try:
            cached_post = await self.redis.get(f"post:{post_id}")
            if cached_post:
                return ReturnPostDTO.model_validate_json(cached_post)
            post = await self.repository.get_by_id(post_id)
            if post is None:
                raise PostNotFoundError
            logger.info(f"Got post with id {post_id}")
            res_post = ReturnPostDTO.model_validate(post)
            await self.redis.set(f"post:{post_id}", res_post.model_dump_json())
            return res_post
        except RedisError:
            logger.exception(f"Failed to get post with id {post_id}")
            raise CacheError
        except SQLAlchemyError:
            logger.exception(f"Failed to get post with id {post_id}")
            raise DatabaseError

    async def update_post(
        self, post_id: int, post_data: UpdatePostDTO
    ) -> ReturnPostDTO:
        """Обновление поста в бд и кеше."""
        try:
            post = await self.repository.update_post(post_id, post_data)
            if post is None:
                raise PostNotFoundError
            logger.info(f"Updated post with id {post_id}")
            res_post = ReturnPostDTO.model_validate(post)
            await self.redis.set(f"post:{post_id}", res_post.model_dump_json())
            return res_post
        except RedisError:
            logger.exception(f"Failed to update post with id {post_id}")
            raise CacheError
        except SQLAlchemyError:
            logger.exception(f"Failed to update post with id {post_id}")
            raise DatabaseError

    async def delete_post(self, post_id: int) -> ReturnPostDTO:
        """Удаление поста из бд и кеша."""
        try:
            post = await self.repository.delete_post(post_id)
            if post is None:
                raise PostNotFoundError
            logger.info(f"Deleted post with id {post_id}")
            await self.redis.delete(f"post:{post_id}")
            return ReturnPostDTO.model_validate(post)
        except RedisError:
            logger.exception(f"Failed to delete post with id {post_id}")
            raise CacheError
        except SQLAlchemyError:
            logger.exception(f"Failed to delete post with id {post_id}")
            raise DatabaseError

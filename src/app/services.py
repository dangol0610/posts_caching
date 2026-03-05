from redis.asyncio import Redis

from src.app.repository import PostsRepository


class PostsService:
    """Service для работы с постами."""

    def __init__(self, repository: PostsRepository, redis: Redis):
        self.repository = repository
        self.redis = redis

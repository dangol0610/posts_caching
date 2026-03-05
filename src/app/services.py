from src.app.repository import PostsRepository


class PostsService:
    """Service для работы с постами."""

    def __init__(self, repository: PostsRepository):
        self.repository = repository

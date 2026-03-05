class PostServiceError(Exception):
    """Базовое исключение для ошибок сервиса постов."""

    pass


class PostNotFoundError(PostServiceError):
    """Исключение, возникающее при попытке найти несуществующий пост."""

    pass


class PostAlreadyExistsError(PostServiceError):
    """Исключение, возникающее при попытке создать существующий пост."""

    pass


class DatabaseError(PostServiceError):
    """Исключение, возникающее при ошибке в базе данных."""

    pass


class CacheError(PostServiceError):
    """Исключение, возникающее при ошибке в кеше."""

    pass

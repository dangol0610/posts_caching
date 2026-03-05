from pydantic import BaseModel, ConfigDict


class CreatePostDTO(BaseModel):
    """DTO для создания поста"""

    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class ReturnPostDTO(BaseModel):
    """DTO для возвращения поста"""

    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class UpdatePostDTO(BaseModel):
    """DTO для обновления поста"""

    title: str | None = None
    content: str | None = None

    model_config = ConfigDict(from_attributes=True)

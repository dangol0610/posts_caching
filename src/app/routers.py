from fastapi import APIRouter, HTTPException, status

from src.app.schemas import CreatePostDTO, ReturnPostDTO, UpdatePostDTO
from src.utils.dependencies import ServiceDependency
from src.utils.exceptions import CacheError, DatabaseError, PostNotFoundError

router = APIRouter(tags=["Posts"], prefix="/posts")


@router.post(
    "/",
    response_model=ReturnPostDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: CreatePostDTO,
    service: ServiceDependency,
) -> ReturnPostDTO:
    """
    Создание нового поста.
    """
    try:
        post_return = await service.create_post(post)
        return post_return
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Service error"
        )


@router.get(
    "/{post_id}",
    response_model=ReturnPostDTO,
    status_code=status.HTTP_200_OK,
)
async def get_post(
    post_id: int,
    service: ServiceDependency,
) -> ReturnPostDTO:
    """
    Получение поста по ID.
    """
    try:
        post = await service.get_post_by_id(post_id)
        return post
    except PostNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Service error"
        )
    except CacheError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Service error"
        )


@router.patch(
    "/{post_id}",
    response_model=ReturnPostDTO,
    status_code=status.HTTP_200_OK,
)
async def update_post(
    post_id: int,
    post: UpdatePostDTO,
    service: ServiceDependency,
) -> ReturnPostDTO:
    """
    Обновление поста по ID.
    """
    try:
        post_return = await service.update_post(post_id, post)
        return post_return
    except PostNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Service error"
        )
    except CacheError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Service error"
        )


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReturnPostDTO,
)
async def delete_post(
    post_id: int,
    service: ServiceDependency,
) -> ReturnPostDTO:
    """
    Удаление поста по ID.
    """
    try:
        deleted_post = await service.delete_post(post_id)
        return deleted_post
    except PostNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Service error"
        )
    except CacheError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Service error"
        )

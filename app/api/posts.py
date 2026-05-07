from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_post_service
from app.models.user import User
from app.schemas.post import PostCreate, PostRead, PostUpdate
from app.services.post import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    """Создание нового поста."""
    return await post_service.create_post(
        current_user=current_user,
        data=data,
    )


@router.get("", response_model=list[PostRead])
async def get_posts(
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    """Получение списка постов. Администратор может получать все посты, обычный пользователь - только свои."""
    return await post_service.get_posts(current_user=current_user)


@router.get("/{post_id}", response_model=PostRead)
async def get_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    """Получение поста по ID. Администратор может получать любые посты, обычный пользователь - только свои."""
    return await post_service.get_post(
        current_user=current_user,
        post_id=post_id,
    )


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    data: PostUpdate,
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    """Изменение поста. Администратор может изменять любые посты, обычный пользователь - только свои."""
    return await post_service.update_post(
        current_user=current_user,
        post_id=post_id,
        data=data,
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    """Удаление поста. Администратор может удалять любые посты, обычный пользователь - только свои."""
    await post_service.delete_post(
        current_user=current_user,
        post_id=post_id,
    )

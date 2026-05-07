from fastapi import APIRouter, Depends
from starlette import status

from app.models import User
from app.schemas.user import UserOut, UserUpdate
from app.services.user import UserService
from app.api.deps import get_current_user, get_user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе."""
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """Изменить текущего пользователя."""
    return await user_service.update_user(
        current_user=current_user,
        data=data,
        user_id=current_user.id,
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """Удаление текущего пользователя."""
    await user_service.delete_user(current_user=current_user, user_id=current_user.id)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """Изменение пользователя."""
    return await user_service.update_user(
        current_user=current_user,
        user_id=user_id,
        data=data,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """Удаление пользователя."""
    await user_service.delete_user(
        current_user=current_user,
        user_id=user_id,
    )

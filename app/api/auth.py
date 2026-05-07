from fastapi import APIRouter, Depends
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service
from app.api.deps import get_user_service
from app.core.security import oauth2_scheme
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserOut
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(request_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    """Регистрация нового пользователя."""
    user = await user_service.register(data=request_data)
    return user


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Аутентификация пользователя и выдача JWT токена.

    Принимает email и пароль, проверяет их и возвращает токен доступа.
    """
    return await auth_service.login(
        email=form_data.username,
        password=form_data.password,
    )


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Выход из системы. Добавляет токен в черный список, чтобы он больше не был действительным."""
    await auth_service.logout(token=token)

    return {"detail": "Successfully logged out"}

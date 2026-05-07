from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.exc import SQLAlchemyError

from app.models.role import RoleEnum
from app.models.user import User
from app.core.config import settings
from app.core.logger import logger
from app.core.security import oauth2_scheme
from app.db.session import AsyncSessionLocal
from app.repositories.access import AccessRepository
from app.repositories.auth import AuthRepository
from app.repositories.post import PostRepository
from app.repositories.user import UserRepository
from app.services.access import AccessService
from app.services.auth import AuthService
from app.services.post import PostService
from app.services.user import UserService


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(UserRepository),
    auth_repository: AuthRepository = Depends(AuthRepository),
) -> User:
    """Получение текущего пользователя из JWT токена."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id_raw = payload.get("sub")

        if user_id_raw is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        user_id = int(user_id_raw)

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    async with AsyncSessionLocal() as session:
        try:
            is_revoked = await auth_repository.is_token_revoked(
                session=session,
                token=token,
            )

            if is_revoked:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token revoked, please log in",
                )

            user = await user_repository.get_by_id(
                session=session,
                user_id=user_id,
            )

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User is inactive",
                )

            return user

        except SQLAlchemyError as e:
            logger.error("DB error while getting current user", error=repr(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="DB error while getting current user",
            )


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение текущего пользователя и проверка его роли - должен быть администратор."""
    if current_user.role.name != RoleEnum.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required",
        )

    return current_user


def get_user_service() -> UserService:
    """Получение сервиса управления пользователями."""
    return UserService(
        session_generator=AsyncSessionLocal,
        user_repository=UserRepository(),
        access_repository=AccessRepository(),
        logger=logger,
    )


def get_post_service() -> PostService:
    """Получение сервиса управления постами."""
    return PostService(
        session_generator=AsyncSessionLocal,
        post_repository=PostRepository(),
        access_repository=AccessRepository(),
        logger=logger,
    )


def get_access_service() -> AccessService:
    """Получение сервиса управления доступом."""
    return AccessService(
        session_generator=AsyncSessionLocal,
        access_repository=AccessRepository(),
        logger=logger,
    )


def get_auth_service() -> AuthService:
    """Получение сервиса аутентификации."""
    return AuthService(
        session_generator=AsyncSessionLocal,
        user_repository=UserRepository(),
        auth_repository=AuthRepository(),
        logger=logger,
    )

from datetime import datetime

from fastapi import HTTPException
from jose import jwt
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.repositories.auth import AuthRepository
from app.repositories.user import UserRepository


class AuthService:
    def __init__(
        self,
        session_generator,
        user_repository: UserRepository,
        auth_repository: AuthRepository,
        logger,
    ):
        self.session_generator = session_generator
        self.user_repository = user_repository
        self.auth_repository = auth_repository
        self.logger = logger

    async def login(self, email: str, password: str) -> dict[str, str]:
        """Аутентификация пользователя - проверяем email и пароль, если все верно - выдаем JWT токен."""
        async with self.session_generator() as session:
            try:
                user = await self.user_repository.get_by_email(
                    session=session,
                    email=email,
                )

                if user is None or not verify_password(password, user.password_hash):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password",
                    )

                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User is inactive contact administrator",
                    )

                access_token = create_access_token(subject=str(user.id))

                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                }

            except SQLAlchemyError as e:
                self.logger.error("DB error while login", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while login",
                )

    async def logout(self, token: str) -> None:
        """Выход из системы - добавляем токен в черный список, чтобы он больше не был валидным."""
        async with self.session_generator() as session:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            exp = payload.get("exp")

            is_revoked = await self.auth_repository.is_token_revoked(
                session=session,
                token=token,
            )

            if is_revoked:
                return

            await self.auth_repository.revoke_token(
                session=session,
                token=token,
                expires_at=datetime.fromtimestamp(exp),
            )

            await session.commit()

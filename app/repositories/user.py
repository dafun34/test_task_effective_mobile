from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Role
from app.models.role import RoleEnum
from app.schemas.user import UserUpdate


class UserRepository:
    async def get_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        """Получает пользователя по его идентификатору.

        Если пользователь с таким идентификатором не найден, возвращает None.
        """
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        """Получает пользователя по его email. Если пользователь с таким email не найден, возвращает None."""
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_default_role_id(self, session: AsyncSession) -> int | None:
        """Получает идентификатор роли по умолчанию для новых пользователей. В данном случае, это роль USER."""
        result = await session.execute(select(Role.id).where(Role.name == RoleEnum.USER.value))
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str | None,
        middle_name: str | None,
        role_id: int,
    ) -> User:
        """Создает нового пользователя с указанными данными и сохраняет его в базе данных."""
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            role_id=role_id,
        )

        session.add(user)
        await session.flush()
        await session.refresh(user)

        return user

    async def update_user(self, session: AsyncSession, user: User, data: UserUpdate) -> User:
        """Обновляет данные пользователя на основе переданных данных.

        Только поля, которые были изменены, будут обновлены.
        """
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        await session.flush()
        await session.refresh(user)

        return user

    async def deactivate_user(self, session: AsyncSession, user: User) -> User:
        """Деактивирует пользователя, устанавливая флаг is_active в False."""
        user.is_active = False

        await session.flush()
        await session.refresh(user)

        return user

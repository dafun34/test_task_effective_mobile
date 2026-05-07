from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.core.security import hash_password
from app.models import User
from app.models.role import PermissionAction, BusinessElementName
from app.repositories.access import AccessRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.permissions import check_permission


class UserService:
    def __init__(self, session_generator, user_repository: UserRepository, logger, access_repository: AccessRepository):
        self.session_generator = session_generator
        self.user_repository = user_repository
        self.access_repository = access_repository
        self.logger = logger

    async def register(self, data: UserCreate) -> User:
        """Регистрация нового пользователя."""
        if data.password != data.password_repeat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match",
            )

        async with self.session_generator() as session:
            try:
                existing_user = await self.user_repository.get_by_email(
                    session=session,
                    email=data.email,
                )

                if existing_user is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User already exists",
                    )

                role_id = await self.user_repository.get_default_role_id(
                    session=session,
                )

                if role_id is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Default user role not found",
                    )

                user = await self.user_repository.create(
                    session=session,
                    email=data.email,
                    password_hash=hash_password(data.password),
                    first_name=data.first_name,
                    last_name=data.last_name,
                    middle_name=data.middle_name,
                    role_id=role_id,
                )

                await session.commit()

                return user

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error("DB error while registering user", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while registering user",
                )

    async def update_user(self, current_user: User, user_id: int, data: UserUpdate) -> User:
        """Обновление данных пользователя.

        Администратор может обновлять любого пользователя, обычный пользователь - только свои данные.
        """
        async with self.session_generator() as session:
            try:
                target_user = await self.user_repository.get_by_id(
                    session=session,
                    user_id=user_id,
                )

                if target_user is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )

                rule = await self.access_repository.get_access_rule(
                    session=session,
                    role_id=current_user.role_id,
                    element_name=BusinessElementName.USERS,
                )

                check_permission(
                    user=current_user,
                    rule=rule,
                    action=PermissionAction.UPDATE,
                    owner_id=target_user.id,
                )

                updated_user = await self.user_repository.update_user(
                    session=session,
                    user=target_user,
                    data=data,
                )

                await session.commit()
                return updated_user

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error("DB error while updating user", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while updating user",
                )

    async def delete_user(self, current_user: User, user_id: int) -> None:
        """Деактивировать пользователя (soft delete)."""
        async with self.session_generator() as session:
            try:
                target_user = await self.user_repository.get_by_id(
                    session=session,
                    user_id=user_id,
                )

                if target_user is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )

                rule = await self.access_repository.get_access_rule(
                    session=session,
                    role_id=current_user.role_id,
                    element_name=BusinessElementName.USERS,
                )

                check_permission(
                    user=current_user,
                    rule=rule,
                    action=PermissionAction.DELETE,
                    owner_id=target_user.id,
                )

                await self.user_repository.deactivate_user(
                    session=session,
                    user=target_user,
                )

                await session.commit()

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error("DB error while deleting user", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while deleting user",
                )

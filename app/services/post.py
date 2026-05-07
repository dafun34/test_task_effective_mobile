from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.models import User, Post
from app.models.role import PermissionAction, BusinessElementName
from app.repositories.post import PostRepository
from app.repositories.access import AccessRepository
from app.schemas.post import PostCreate, PostUpdate
from app.services.permissions import check_permission


class PostService:
    def __init__(
        self,
        session_generator,
        post_repository: PostRepository,
        access_repository: AccessRepository,
        logger,
    ):
        self.session_generator = session_generator
        self.post_repository = post_repository
        self.access_repository = access_repository
        self.logger = logger

    async def create_post(self, current_user: User, data: PostCreate) -> Post:
        """Создание нового поста.

        Администратор может создавать посты от имени любого пользователя,
        обычный пользователь - только от своего имени.
        """
        async with self.session_generator() as session:
            try:
                rule = await self.access_repository.get_access_rule(
                    session=session,
                    role_id=current_user.role_id,
                    element_name=BusinessElementName.POSTS,
                )

                check_permission(
                    user=current_user,
                    rule=rule,
                    action=PermissionAction.CREATE,
                )

                post = await self.post_repository.create(
                    session=session,
                    title=data.title,
                    content=data.content,
                    owner_id=current_user.id,
                )

                await session.commit()
                return post

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error("DB error while creating post", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while creating post",
                )

    async def get_post(self, current_user: User, post_id: int) -> Post:
        """Получение поста по ID.

        Администратор может получать любой пост, обычный пользователь - только свои посты.
        """
        async with self.session_generator() as session:
            try:
                post = await self.post_repository.get_by_id(
                    session=session,
                    post_id=post_id,
                )

                if post is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Post not found",
                    )

                rule = await self.access_repository.get_access_rule(
                    session=session,
                    role_id=current_user.role_id,
                    element_name=BusinessElementName.POSTS,
                )

                check_permission(
                    user=current_user,
                    rule=rule,
                    action=PermissionAction.READ,
                    owner_id=post.owner_id,
                )

                return post

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error("DB error while fetching post", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while fetching post",
                )

    async def get_posts(self, current_user: User) -> list[Post]:
        """Получение списка постов."""
        async with self.session_generator() as session:
            try:
                rule = await self.access_repository.get_access_rule(
                    session=session,
                    role_id=current_user.role_id,
                    element_name=BusinessElementName.POSTS,
                )

                if rule is None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Permission rule not found",
                    )

                if rule.read_all_permission:
                    return await self.post_repository.get_all(session=session)

                if rule.read_permission:
                    return await self.post_repository.get_by_owner_id(
                        session=session,
                        owner_id=current_user.id,
                    )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                )

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error("DB error while fetching posts", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while fetching posts",
                )

    async def update_post(self, current_user: User, data: PostUpdate, post_id: int) -> Post:
        """Обновление поста.

        Администратор может обновлять любой пост, обычный пользователь - только свои посты.
        """
        async with self.session_generator() as session:
            try:
                post = await self.post_repository.get_by_id(
                    session=session,
                    post_id=post_id,
                )

                if post is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Post not found",
                    )

                rule = await self.access_repository.get_access_rule(
                    session=session,
                    role_id=current_user.role_id,
                    element_name=BusinessElementName.POSTS,
                )

                check_permission(
                    user=current_user,
                    rule=rule,
                    action=PermissionAction.UPDATE,
                    owner_id=post.owner_id,
                )

                update_data = data.model_dump(exclude_unset=True)

                for field, value in update_data.items():
                    setattr(post, field, value)

                await session.commit()
                await session.refresh(post)

                return post

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error("DB error while updating post", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while updating post",
                )

    async def delete_post(self, current_user: User, post_id: int) -> None:
        """Удаление поста.

        Администратор может удалять любой пост, обычный пользователь - только свои посты.
        """
        async with self.session_generator() as session:
            try:
                post = await self.post_repository.get_by_id(
                    session=session,
                    post_id=post_id,
                )

                if post is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Post not found",
                    )

                rule = await self.access_repository.get_access_rule(
                    session=session,
                    role_id=current_user.role_id,
                    element_name=BusinessElementName.POSTS,
                )

                check_permission(
                    user=current_user,
                    rule=rule,
                    action=PermissionAction.DELETE,
                    owner_id=post.owner_id,
                )

                await self.post_repository.delete(session=session, post=post)
                await session.commit()

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error("DB error while deleting post", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while deleting post",
                )

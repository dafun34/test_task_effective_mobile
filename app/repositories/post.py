from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.models import Post


class PostRepository:
    async def create(
        self,
        session: AsyncSession,
        title: str,
        content: str,
        owner_id: int,
    ) -> Post:
        """Создание нового поста. Уникальность поста определяется сочетанием заголовка и владельца."""
        try:
            post = Post(
                title=title,
                content=content,
                owner_id=owner_id,
            )

            session.add(post)
            await session.flush()
            await session.refresh(post)

            return post
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_by_id(self, session: AsyncSession, post_id: int) -> Post | None:
        """Получение поста по ID."""
        result = await session.execute(select(Post).where(Post.id == post_id))
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> list[Post]:
        """Получить все посты."""
        result = await session.execute(select(Post))
        return list(result.scalars().all())

    async def get_by_owner_id(self, session: AsyncSession, owner_id: int) -> list[Post]:
        """Получение всех постов, принадлежащих пользователю с указанным owner_id."""
        result = await session.execute(select(Post).where(Post.owner_id == owner_id))
        return list(result.scalars().all())

    async def delete(self, session: AsyncSession, post: Post) -> None:
        """Удаление поста из БД."""
        await session.delete(post)
        await session.flush()

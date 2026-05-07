from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revoked_token import RevokedToken


class AuthRepository:
    async def is_token_revoked(self, session: AsyncSession, token: str) -> bool:
        """Проверка, отозван ли токен. Возвращает True, если токен найден в списке отозванных, иначе False."""
        result = await session.execute(select(RevokedToken).where(RevokedToken.token == token))

        return result.scalar_one_or_none() is not None

    async def revoke_token(self, session: AsyncSession, token: str, expires_at) -> None:
        """Добавление токена в список отозванных."""
        revoked_token = RevokedToken(token=token, expires_at=expires_at)
        session.add(revoked_token)

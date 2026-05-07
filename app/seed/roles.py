from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.role import Role


async def get_or_create_role(db: AsyncSession, name: str, description: str) -> Role:
    """Получение или создание роли."""
    result = await db.execute(select(Role).where(Role.name == name))
    role = result.scalar_one_or_none()

    if role:
        logger.debug("role already exists", name=name, description=description)
        return role

    role = Role(name=name, description=description)
    db.add(role)
    await db.flush()
    logger.info("role successful created", name=name, description=description)
    return role

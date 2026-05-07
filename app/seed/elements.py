from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.role import BusinessElement


async def get_or_create_element(db: AsyncSession, name: str, description: str) -> BusinessElement:
    """Получение или создание элемента."""
    result = await db.execute(select(BusinessElement).where(BusinessElement.name == name))
    element = result.scalar_one_or_none()

    if element:
        logger.debug("element already exists", name=name, description=description)
        return element

    element = BusinessElement(name=name, description=description)
    db.add(element)
    await db.flush()
    logger.debug("element created", code=name, name=description)
    return element

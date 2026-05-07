from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import AccessRoleRule
from app.core.logger import logger


async def create_or_update_rule(db: AsyncSession, role_id: int, element_id: int, **permissions) -> AccessRoleRule:
    """Получение или создание правила доступа."""
    result = await db.execute(
        select(AccessRoleRule).where(
            AccessRoleRule.role_id == role_id,
            AccessRoleRule.element_id == element_id,
        )
    )
    rule = result.scalar_one_or_none()

    if rule is None:
        rule = AccessRoleRule(
            role_id=role_id,
            element_id=element_id,
        )
        db.add(rule)

    for key, value in permissions.items():
        setattr(rule, key, value)
    logger.debug("rule created/updated successful", element_id=element_id, permissions=permissions)
    return rule

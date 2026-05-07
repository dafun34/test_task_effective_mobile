from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import AccessRoleRule
from app.models.role import BusinessElement, BusinessElementName
from app.schemas.access import AccessRuleUpdate


class AccessRepository:
    async def get_all_rules(self, session: AsyncSession) -> list[AccessRoleRule]:
        """Получение всех правил доступа.

        Возвращает список AccessRoleRule с загруженными данными о ролях и элементах.
        """
        result = await session.execute(
            select(AccessRoleRule).options(
                selectinload(AccessRoleRule.role),
                selectinload(AccessRoleRule.element),
            )
        )
        return list(result.scalars().all())

    async def get_rule_by_id(
        self,
        session: AsyncSession,
        rule_id: int,
    ) -> AccessRoleRule | None:
        """Получение правила доступа по его ID. Возвращает AccessRoleRule, если правило найдено, иначе None."""
        result = await session.execute(
            select(AccessRoleRule)
            .options(
                selectinload(AccessRoleRule.role),
                selectinload(AccessRoleRule.element),
            )
            .where(AccessRoleRule.id == rule_id)
        )

        return result.scalar_one_or_none()

    async def get_access_rule(
        self, session: AsyncSession, role_id: int, element_name: BusinessElementName
    ) -> AccessRoleRule | None:
        """Получение правила доступа для заданной роли и элемента.

        Возвращает AccessRoleRule, если правило найдено, иначе None.
        """
        result = await session.execute(
            select(AccessRoleRule)
            .join(BusinessElement, BusinessElement.id == AccessRoleRule.element_id)
            .where(
                AccessRoleRule.role_id == role_id,
                BusinessElement.name == element_name.value,
            )
        )

        return result.scalar_one_or_none()

    async def update_rule(self, session: AsyncSession, rule: AccessRoleRule, data: AccessRuleUpdate) -> None:
        """Обновление существующего правила доступа. Только те поля, которые были переданы в data, будут обновлены."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(rule, field, value)

        await session.flush()

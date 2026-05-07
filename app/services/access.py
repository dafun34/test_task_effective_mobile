from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.models.role import AccessRoleRule
from app.repositories.access import AccessRepository
from app.schemas.access import AccessRuleUpdate


class AccessService:
    def __init__(self, session_generator, access_repository: AccessRepository, logger):
        self.session_generator = session_generator
        self.access_repository = access_repository
        self.logger = logger

    async def get_rules(self) -> list[AccessRoleRule]:
        """Получение всех правил доступа."""
        async with self.session_generator() as session:
            try:
                return await self.access_repository.get_all_rules(session=session)

            except SQLAlchemyError as e:
                self.logger.error("DB error while fetching access rules", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while fetching access rules",
                )

    async def update_rule(
        self,
        rule_id: int,
        data: AccessRuleUpdate,
    ) -> AccessRoleRule:
        """Обновление правила доступа.

        Администратор может обновлять любое правило, обычный пользователь - не может обновлять правила.
        """
        async with self.session_generator() as session:
            try:
                rule = await self.access_repository.get_rule_by_id(
                    session=session,
                    rule_id=rule_id,
                )

                if rule is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Access rule not found",
                    )

                await self.access_repository.update_rule(
                    session=session,
                    rule=rule,
                    data=data,
                )

                await session.commit()

                updated_rule = await self.access_repository.get_rule_by_id(
                    session=session,
                    rule_id=rule_id,
                )

                return updated_rule

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error("DB error while updating access rule", error=repr(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error while updating access rule",
                )

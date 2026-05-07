from fastapi import APIRouter, Depends

from app.models import User
from app.schemas.access import AccessRuleRead, AccessRuleUpdate
from app.services.access import AccessService
from app.api.deps import get_admin_user, get_access_service

router = APIRouter(prefix="/access-rules", tags=["Access rules"])


@router.get("", response_model=list[AccessRuleRead])
async def get_access_rules(
    access_service: AccessService = Depends(get_access_service),
    admin: User = Depends(get_admin_user),
):
    """Получение списка правил доступа. Только администратор может получать список правил доступа."""
    return await access_service.get_rules()


@router.patch("/{rule_id}", response_model=AccessRuleRead)
async def update_access_rule(
    rule_id: int,
    data: AccessRuleUpdate,
    access_service: AccessService = Depends(get_access_service),
    admin: User = Depends(get_admin_user),
):
    """Изменение правила доступа. Только администратор может изменять правила доступа."""
    return await access_service.update_rule(
        rule_id=rule_id,
        data=data,
    )

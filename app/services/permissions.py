from fastapi import HTTPException
from starlette import status

from app.models import User
from app.models.role import AccessRoleRule
from app.models.role import PermissionAction


def check_permission(
    user: User,
    rule: AccessRoleRule | None,
    action: PermissionAction,
    owner_id: int | None = None,
) -> None:
    """Проверить права доступа для пользователя и действия над бизнес-элементом."""
    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission rule not found",
        )

    if action == PermissionAction.CREATE:
        if not rule.create_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return

    if owner_id is None:
        raise ValueError("owner_id is required for read/update/delete actions")

    is_owner = owner_id == user.id

    if action == PermissionAction.READ:
        allowed = rule.read_permission if is_owner else rule.read_all_permission
    elif action == PermissionAction.UPDATE:
        allowed = rule.update_permission if is_owner else rule.update_all_permission
    elif action == PermissionAction.DELETE:
        allowed = rule.delete_permission if is_owner else rule.delete_all_permission
    else:
        raise ValueError(f"Unknown action: {action}")

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

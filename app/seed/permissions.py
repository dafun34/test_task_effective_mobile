from sqlalchemy.ext.asyncio import AsyncSession

from app.seed.elements import get_or_create_element
from app.seed.roles import get_or_create_role
from app.seed.rules import create_or_update_rule


async def seed_permissions(db: AsyncSession) -> None:
    """Заполнить БД начальными данными для ролей, элементов и правил доступа."""
    admin = await get_or_create_role(db, "admin", "Администратор")
    user = await get_or_create_role(db, "user", "Пользователь")

    users = await get_or_create_element(db, "users", "Пользователи")
    posts = await get_or_create_element(db, "posts", "Посты")

    # admin → всё
    await create_or_update_rule(
        db,
        admin.id,
        users.id,
        read_permission=True,
        read_all_permission=True,
        create_permission=True,
        update_permission=True,
        update_all_permission=True,
        delete_permission=True,
        delete_all_permission=True,
    )

    await create_or_update_rule(
        db,
        admin.id,
        posts.id,
        read_permission=True,
        read_all_permission=True,
        create_permission=True,
        update_permission=True,
        update_all_permission=True,
        delete_permission=True,
        delete_all_permission=True,
    )

    # user
    await create_or_update_rule(
        db,
        user.id,
        users.id,
        read_permission=True,
        update_permission=True,
        delete_permission=True,
    )

    await create_or_update_rule(
        db,
        user.id,
        posts.id,
        read_permission=True,
        create_permission=True,
        update_permission=True,
        delete_permission=True,
    )

    await db.commit()

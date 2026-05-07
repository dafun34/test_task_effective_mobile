from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User, Post, Role


async def seed_demo_data(db: AsyncSession) -> None:
    """Заполнить БД тестовыми данными: создать админа, двух пользователей и по посту от каждого пользователя."""
    admin_role = await get_role(db, "admin")
    user_role = await get_role(db, "user")

    await get_or_create_user(
        db,
        email="admin@example.com",
        password="admin123",
        first_name="Admin",
        role_id=admin_role.id,
    )

    user1 = await get_or_create_user(
        db,
        email="user1@example.com",
        password="user123",
        first_name="User1",
        role_id=user_role.id,
    )

    user2 = await get_or_create_user(
        db,
        email="user2@example.com",
        password="user123",
        first_name="User2",
        role_id=user_role.id,
    )

    await get_or_create_post(
        db,
        title="User1 post",
        content="Post created by user1",
        owner_id=user1.id,
    )

    await get_or_create_post(
        db,
        title="User2 post",
        content="Post created by user2",
        owner_id=user2.id,
    )

    await db.commit()


async def get_role(db: AsyncSession, name: str) -> Role:
    """Получение роли по имени."""
    result = await db.execute(select(Role).where(Role.name == name))
    role = result.scalar_one_or_none()

    if role is None:
        raise RuntimeError(f"Role '{name}' not found. Run permissions seed first.")

    return role


async def get_or_create_user(
    db: AsyncSession,
    email: str,
    password: str,
    first_name: str,
    role_id: int,
) -> User:
    """Получение или создание пользователя. Уникальность пользователя определяется email."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is not None:
        return user

    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=None,
        middle_name=None,
        role_id=role_id,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


async def get_or_create_post(
    db: AsyncSession,
    title: str,
    content: str,
    owner_id: int,
) -> Post:
    """Получение или создание поста. Уникальность поста определяется сочетанием заголовка и владельца."""
    result = await db.execute(
        select(Post).where(
            Post.title == title,
            Post.owner_id == owner_id,
        )
    )
    post = result.scalar_one_or_none()

    if post is not None:
        return post

    post = Post(
        title=title,
        content=content,
        owner_id=owner_id,
    )

    db.add(post)
    await db.flush()
    await db.refresh(post)

    return post

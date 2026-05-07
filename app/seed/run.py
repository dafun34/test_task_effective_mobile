import asyncio

from app.db.session import AsyncSessionLocal
from app.seed.permissions import seed_permissions
from app.seed.demo import seed_demo_data
from app.core.logger import logger


async def main() -> None:
    """Заполнить БД тестовыми данными."""
    async with AsyncSessionLocal() as db:
        logger.info("Database seeding started.")
        await seed_permissions(db)
        await seed_demo_data(db)
        logger.info("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())

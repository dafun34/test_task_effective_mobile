from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from app.api import auth
from app.api import posts
from app.api import access
from app.api import users
from app.core.config import settings
from app.db.session import run_migrations
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения."""
    run_migrations()
    logger.info(f"{settings.APP_TITLE} started on {settings.APP_HOST}:{settings.APP_PORT}")
    yield


app = FastAPI(lifespan=lifespan, title=settings.APP_TITLE, description="Тестовое задание для компании Funtech")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(access.router)
app.include_router(posts.router)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)

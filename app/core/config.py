from functools import lru_cache
from typing import Annotated

from dotenv import find_dotenv
from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")
    # app
    APP_TITLE: str = Field(description="Application title", default="Auth Service")
    APP_HOST: str
    APP_PORT: int
    # postgres
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="postgres")
    # logger
    LOGGING_LEVEL: str = Field(description="Logging level", default="DEBUG")
    # security
    SECRET_KEY: str = Field(description="Secret key for JWT")
    ALGORITHM: str = Field(description="Algorithm for JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(description="Access token expire time in minutes", default=30)
    # sqlalchemy
    ENGINE_ECHO: bool = Field(description="Enable debug logging", default=False)

    @property
    def postgres_connection_string(self) -> str:
        """Формирование строки подключения к PostgreSQL."""
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )


@lru_cache
def get_settings():
    """Получение настроек приложения с кэшированием."""
    return Settings()


settings = get_settings()

SettingsDependency = Annotated[Settings, Depends(get_settings)]

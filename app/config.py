import os
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

basedir = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"

    model_config = SettingsConfigDict(
        env_file=os.path.join(basedir, "..", ".env")
    )


settings = Settings()

log_file_path = os.path.join(basedir, "log.txt")
logger.add(log_file_path, format=settings.FORMAT_LOG, level="INFO", rotation=settings.LOG_ROTATION)

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:"
    f"{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

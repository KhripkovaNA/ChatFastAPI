import os
from pydantic_settings import BaseSettings, SettingsConfigDict

basedir = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(basedir, "..", ".env")
    )


settings = Settings()

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:"
    f"{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)


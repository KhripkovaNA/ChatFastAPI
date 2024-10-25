import os
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

basedir = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"

    bot_token: str
    base_webhook_url: str
    webhook_path: str = "/webhook"
    telegram_my_token: str
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=os.path.join(basedir, "..", ".env")
    )

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()

log_file_path = os.path.join(basedir, "..",  "log.txt")
logger.add(
    log_file_path, format=settings.FORMAT_LOG, rotation=settings.LOG_ROTATION, retention="7 days", compression="zip"
)


def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}

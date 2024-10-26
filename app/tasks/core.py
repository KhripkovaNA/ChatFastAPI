from celery import Celery
from app.config import settings as cfg

celery = Celery(
    "tasks",
    broker=f"redis://{cfg.REDIS_HOST}:{cfg.REDIS_PORT}",
    include=["app.tasks.tasks"]
)

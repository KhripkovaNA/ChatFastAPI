from app.bot.bot import send_message_by_user_id
from app.tasks.core import celery
import asyncio
from loguru import logger


@celery.task
def create_task_send_message(tg_id: str, text: str) -> None:
    try:
        asyncio.run(send_message_by_user_id(tg_id, text))
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_message_by_user_id(tg_id, text))
    except Exception as e:
        logger.error(repr(e))

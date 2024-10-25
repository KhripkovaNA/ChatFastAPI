from typing import Annotated
from fastapi import APIRouter, Header
from loguru import logger
from aiogram import types
from app.bot.bot import bot, dp
from app.config import settings as cfg

router = APIRouter(
    prefix="",
    tags=["Bot"],
    responses={404: {"description": "Not found"}},
)


@router.post(cfg.webhook_path)
async def bot_webhook(
        update: dict,
        x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None
) -> None | dict:
    """ Register webhook endpoint for telegram bot"""
    if x_telegram_bot_api_secret_token != cfg.telegram_my_token:
        logger.error("Неверный secret token")
        return {"status": "error", "message": "Wrong secret token!"}
    telegram_update = types.Update(**update)
    await dp.feed_webhook_update(bot=bot, update=telegram_update)

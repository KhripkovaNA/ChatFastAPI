from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import WebhookInfo, BotCommand
from aiogram.client.default import DefaultBotProperties
from app.bot.handlers import router
from loguru import logger
from app.config import settings as cfg

dp = Dispatcher()

bot = Bot(token=cfg.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp.include_router(router)


async def set_webhook(my_bot: Bot) -> None:
    # Проверить и установить Webhook для Telegram
    async def check_webhook() -> WebhookInfo | None:
        try:
            webhook_info = await my_bot.get_webhook_info()
            return webhook_info
        except Exception as e:
            logger.error(f"Невозможно получить информацию о Webhook - {e}")
            return

    current_webhook_info = await check_webhook()
    if cfg.debug:
        logger.debug(f"Текущая информация о боте: {current_webhook_info}")
    try:
        await my_bot.set_webhook(
            f"{cfg.base_webhook_url}{cfg.webhook_path}",
            secret_token=cfg.telegram_my_token,
            drop_pending_updates=current_webhook_info.pending_update_count > 0,
            max_connections=40 if cfg.debug else 100,
        )
        if cfg.debug:
            logger.debug(f"Обновленная информация о боте: {await check_webhook()}")
    except Exception as e:
        logger.error(f"Не удалось установить Webhook - {e}")


async def set_bot_commands_menu(my_bot: Bot) -> None:
    # Настроить команды для меню Телеграм-бота
    commands = [
        BotCommand(command="/start", description="Перезапуск бота"),
    ]
    try:
        await my_bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Не удалось настроить команды - {e}")


async def send_message_by_user_id(user_id: str, text: str) -> None:
    # Отправить сообщение пользователю по user_id
    try:
        await bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение - {e}")


async def start_telegram():
    if cfg.debug:
        logger.debug("Бот запущен")
    await set_webhook(bot)
    await set_bot_commands_menu(bot)

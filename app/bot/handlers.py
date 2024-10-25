from aiogram.filters import CommandStart
from aiogram import Router, types
from app.config import settings as cfg

router = Router(name="telegram")


@router.message(CommandStart())
async def start(message: types.Message) -> None:
    await message.answer(
        f'Пожалуйста, зарегистрируйтесь/войдите в чат, используя эту ссылку: '
        f'{cfg.base_webhook_url}/auth?tg_id={message.from_user.id}'
    )

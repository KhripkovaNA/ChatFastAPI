from fastapi import WebSocket
import asyncio
from app.bot.bot import send_message_by_user_id
from app.chat.dao import MessagesDAO
from app.chat.schemas import SMessageCreate, SMessageAdd
from app.users.dao import UsersDAO
from app.tasks.tasks import create_task_send_message
from app.users.schemas import SUserRead

# Активные WebSocket-подключения: {user_id: websocket}
active_connections: dict[int, WebSocket] = {}


async def receive_message(message: SMessageCreate, sender: SUserRead) -> list[dict[str, str | int]]:
    # Подготавливаем данные для сохранения и последующей отправки сообщения
    message_data = []

    # Добавляем новое сообщение в базу данных
    if int(message['recipient_id']) == 0:
        if sender.role != 'admin':
            return []
        # Сообщение всем активным пользователям
        for recipient_id in active_connections:
            if recipient_id == sender.id:
                continue
            mes = SMessageAdd(
                sender_id=sender.id,
                recipient_id=recipient_id,
                content=message['content'],
            )
            message_data.append(mes)
    else:
        # Сообщение одному конкретному пользователю
        mes = SMessageAdd(
            sender_id=sender.id,
            recipient_id=message['recipient_id'],
            content=message['content'],
        )
        message_data.append(mes)

    await MessagesDAO.add_many(instances=message_data)

    return [item.model_dump() for item in message_data]


async def send_message(message: dict) -> None:
    # Отправить сообщение пользователю
    sender_id = message.get('sender_id')
    recipient_id = message.get('recipient_id')
    message['type'] = 'message'

    if recipient_id in active_connections:
        websocket = active_connections[recipient_id]
        # Отправляем сообщение в формате JSON
        await websocket.send_json(message)
    else:
        # Уведомить в Телеграм, если пользователь отключен от чата
        recipient = await UsersDAO.find_one_or_none_by_id(recipient_id)
        if recipient and recipient.tg_id:
            sender = await UsersDAO.find_one_or_none_by_id(sender_id)
            create_task_send_message.delay(
                recipient.tg_id,
                f"Новое сообщение в чате от {sender.name}: {message['content']}"
            )
            await send_message_by_user_id(recipient.tg_id, f"New message in chat from user {message['sender_id']}: {message['content']}")


async def send_messages(messages: list[dict]) -> None:
    # Отправить сообщение нескольким пользователям
    tasks = [send_message(message) for message in messages]
    await asyncio.gather(*tasks)


async def send_status_message(user_id: int, is_online: bool) -> None:
    # Отправка сообщения об изменении статуса пользователя в разных потоках
    message = {
        'type': 'status',
        'user_id': user_id,
        'is_online': is_online,
    }

    async def send(websocket):
        await websocket.send_json(message)

    tasks = [send(websocket) for websocket in active_connections.values()]

    await asyncio.gather(*tasks)

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from app.chat.dao import MessagesDAO
from app.chat.dependencies import receive_message, active_connections, send_status_message, send_messages
from app.chat.schemas import SMessageRead
from app.users.dependencies import get_current_user, get_users_with_options
from app.users.schemas import SUserRead

# Создаем экземпляр маршрутизатора с префиксом /chat и тегом "Chat"
router = APIRouter(prefix='/chat', tags=['Chat'])
# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory='app/templates')


# Страница чата
@router.get("/", response_class=HTMLResponse, summary="Страница чата")
async def get_chat_page(request: Request, user_data: SUserRead = Depends(get_current_user)):
    # Получаем всех пользователей из базы данных
    users_all = await get_users_with_options(user_data.id)
    # Возвращаем HTML-страницу с использованием шаблона Jinja2
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "user": user_data, 'users_all': users_all}
    )


# WebSocket эндпоинт для соединений
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             current_user: SUserRead = Depends(get_current_user)):
    # Принимаем WebSocket-соединение
    await websocket.accept()
    # Сохраняем активное соединение для пользователя
    active_connections[current_user.id] = websocket
    # Отправляем всем активным соединениям сообщение о смене статуса пользователя
    await send_status_message(current_user.id, is_online=True)
    try:
        while True:
            # Ждем сообщение
            data = await websocket.receive_json()
            # Обрабатываем полученное сообщение
            messages = await receive_message(data, current_user)
            # Отправляем сообщения
            if messages:
                await send_messages(messages)
    except WebSocketDisconnect:
        # Удаляем пользователя из активных соединений при отключении
        active_connections.pop(current_user.id, None)
        await send_status_message(current_user.id, is_online=False)


# Получение сообщений между двумя пользователями
@router.get("/messages/{user_id}", response_model=List[SMessageRead], summary="Сообщения")
async def get_messages(user_id: int, current_user: SUserRead = Depends(get_current_user)):
    # Помечаем сообщения от пользователя user_id как прочитанные
    await MessagesDAO.mark_messages_as_read(sender_id=user_id, recipient_id=current_user.id)
    # Возвращаем список сообщений между текущим пользователем и другим пользователем
    return await MessagesDAO.get_messages_between_users(user_id_1=user_id, user_id_2=current_user.id) or []


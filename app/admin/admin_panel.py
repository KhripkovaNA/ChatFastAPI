from sqladmin import ModelView, Admin
from app.admin.auth import authentication_backend
from app.database import engine
from app.users.auth import get_password_hash
from app.users.models import Users
from app.chat.models import Messages


class UsersAdmin(ModelView, model=Users):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    # Поля, которые будут отображаться в списке пользователей
    column_list = [Users.id, Users.name, Users.email, Users.role, Users.tg_id]
    # Исключить отображение поля с паролем в деталях пользователя
    column_details_exclude_list = [Users.hashed_password]
    # Отображение поля hashed_password как password
    column_labels = {"hashed_password": "Password"}
    # Отключить возможность удаления пользователей
    can_delete = False
    # Правила для создания и редактирования пользователей
    form_create_rules = ["name", "email", "hashed_password", "role", "tg_id"]
    form_edit_rules = ["name", "email", "role", "tg_id"]

    async def on_model_change(self, data, model, is_created, request) -> None:
        # Хеширование пароля при создании нового пользователя
        if is_created and "hashed_password" in data:
            data["hashed_password"] = get_password_hash(data["hashed_password"])


class MessagesAdmin(ModelView, model=Messages):
    name = "Message"
    name_plural = "Messages"
    icon = "fa-solid fa-message"
    # Поля, которые будут отображаться в списке сообщений
    column_list = [Messages.id, Messages.sender, Messages.recipient, Messages.content]
    # Отключить возможность добавления сообщений
    can_create = False
    # Правила для редактирования сообщений
    form_edit_rules = ["content"]


# Функция инициализации админ-панели
def init_admin(app):
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(UsersAdmin)
    admin.add_view(MessagesAdmin)

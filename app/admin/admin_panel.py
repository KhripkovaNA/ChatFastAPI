from sqladmin import ModelView, Admin
from app.database import engine
from app.users.models import Users


class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.name]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"


# Функция инициализации админ-панели
def init_admin(app):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)

from loguru import logger
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.users.auth import authenticate_user, create_access_token
from app.users.dependencies import get_current_user
from app.users.models import UserRole


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        user = await authenticate_user(email, password)
        if user and user.role == UserRole.admin:
            access_token = create_access_token({"sub": str(user.id), "role": str(user.role)})
            request.session.update({"token": access_token})
            logger.info(f"Вход пользователя {user.email} в админ-панель")
            return True

        if user:
            logger.error(f"Нет прав администратора у {user.email}")
        else:
            logger.error(f"Нет пользователя {email}")
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        token = request.session.get("token")

        if not token:
            logger.error(f"Токен отсутствует")
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        admin_user = await get_current_user(token, is_admin=True)

        if not admin_user:
            logger.error(f"Нет прав администратора")
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        return True


authentication_backend = AdminAuth(secret_key="...")

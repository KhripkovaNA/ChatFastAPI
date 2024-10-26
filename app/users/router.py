from typing import List
from fastapi import APIRouter, Response
from fastapi import Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.errors.exceptions import (
    UserAlreadyExistsException, IncorrectEmailOrPasswordException, PasswordMismatchException
)
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user, get_users_with_options
from app.users.schemas import SUserRegister, SUserAuth, SUserRead, SUserMail, SUserAdd, STelegramID

# Создаем экземпляр маршрутизатора с префиксом /auth и тегом "Auth"
router = APIRouter(prefix='/auth', tags=['Auth'])
# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory='app/templates')


@router.get("/users", response_model=List[SUserRead], summary="Все пользователи")
async def get_users(current_user: SUserRead = Depends(get_current_user)):
    users_all = await get_users_with_options(current_user.id)
    return users_all


@router.get("/", response_class=HTMLResponse, summary="Страница авторизации")
async def get_categories(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@router.post("/register/", summary="Регистрация")
async def register_user(user_data: SUserRegister) -> dict:
    filters = SUserMail(email=user_data.email)
    user = await UsersDAO.find_one_or_none(filters=filters)
    if user:
        raise UserAlreadyExistsException

    if user_data.password != user_data.password_check:
        raise PasswordMismatchException("Пароли не совпадают")
    hashed_password = get_password_hash(user_data.password)
    values = SUserAdd(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        tg_id=user_data.tg_id
    )
    await UsersDAO.add(values=values)

    return {'message': 'Вы успешно зарегистрированы!'}


@router.post("/login/", summary="Авторизация")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise IncorrectEmailOrPasswordException
    if user_data.tg_id:
        filters = SUserMail(email=user_data.email)
        values = STelegramID(tg_id=user_data.tg_id)
        await UsersDAO.update(filters, values)
    access_token = create_access_token({"sub": str(check.id), "role": str(check.role)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Авторизация успешна!'}


@router.post("/logout/", summary="Выход")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

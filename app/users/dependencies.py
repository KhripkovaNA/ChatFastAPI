from fastapi import Request, HTTPException, status, Depends, WebSocket
from jose import jwt, JWTError
from datetime import datetime, timezone
from loguru import logger
from app.chat.dependencies import active_connections
from app.config import get_auth_data
from app.errors.exceptions import TokenExpiredException, NoJwtException, NoUserIdException, TokenNoFoundException
from app.users.dao import UsersDAO
from fastapi_cache.decorator import cache
from app.users.schemas import SUserRead


def get_token(request: Request = None,
              websocket: WebSocket = None):
    token = None

    if request:
        token = request.cookies.get('users_access_token')
    elif websocket:
        token = websocket.cookies.get('users_access_token')

    if not token:
        raise TokenNoFoundException

    return token


@cache(120)
async def get_user_from_db(user_id: int) -> dict:
    user = await UsersDAO.find_one_or_none_by_id(int(user_id))
    return SUserRead.model_validate(user).model_dump()


async def get_current_user(token: str = Depends(get_token), is_admin: bool = False) -> SUserRead:
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=auth_data['algorithm'])
    except JWTError:
        raise NoJwtException

    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise TokenExpiredException

    user_id: str = payload.get('sub')
    if not user_id:
        raise NoUserIdException

    user = await get_user_from_db(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    if is_admin:
        if user["role"] != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Admin user not found')

    return SUserRead(**user)


async def get_users_with_options(user_id: int) -> list[dict]:
    users = await UsersDAO.find_all_with_new_messages(user_id)

    for user in users:
        if user['id'] in active_connections:
            user['is_online'] = True
        else:
            user['is_online'] = False

    return users

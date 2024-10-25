from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from app.errors.exceptions import TokenExpiredException, TokenNoFoundException
from app.errors.handlers import (
    token_expired_exception_handler, token_no_found_exception_handler, global_exception_handler
)
from app.users.router import router as users_router
from app.chat.router import router as chat_router
from app.bot.router import router as bot_router
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.config import settings as cfg
from app.admin.admin_panel import init_admin


@asynccontextmanager
async def lifespan(application: FastAPI):
    redis = aioredis.from_url(f"redis://{cfg.REDIS_HOST}:{cfg.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    from app.bot.bot import start_telegram
    await start_telegram()

    yield


# Инициализация FastAPI приложения с lifespan
app = FastAPI(lifespan=lifespan)

# Инициализация админ-панели
init_admin(app)

# Подключение статики
app.mount('/static', StaticFiles(directory='app/static'), name='static')

# Подключение роутеров
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(bot_router)

# Подключение обработчиков исключений
app.add_exception_handler(TokenExpiredException, token_expired_exception_handler)
app.add_exception_handler(TokenNoFoundException, token_no_found_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


# Редирект на страницу /auth при обращении к корневому маршруту
@app.get("/")
async def redirect_to_auth():
    return RedirectResponse(url="/auth")


# Middleware для логирования всех запросов и ответов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Логируем входящий запрос
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    # Логируем ответ
    logger.info(f"Response status: {response.status_code}")
    return response


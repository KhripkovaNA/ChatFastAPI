from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger


# Обработчик исключений для истекшего токена
async def token_expired_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"Токен просрочен: {exc} на {request.url}")
    return RedirectResponse(url="/auth")


# Обработчик исключений для отсутствующего токена
async def token_no_found_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"Токен не найден: {exc} на {request.url}")
    return RedirectResponse(url="/auth")


# Общий обработчик для всех необработанных исключений
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Ошибка: {exc} на {request.url}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Непредвиденная ошибка"},
    )

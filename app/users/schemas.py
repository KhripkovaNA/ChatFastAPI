from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum


class SUserRole(str, Enum):
    admin = "admin"
    user = "user"


class SUserMail(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")


class STelegramID(BaseModel):
    tg_id: str


class SUserRegister(SUserMail):
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    password_check: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    tg_id: str | None = None


class SUserAdd(SUserMail):
    hashed_password: str
    name: str
    tg_id: str | None = None


class SUserAuth(SUserMail):
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    tg_id: str | None = None


class SUserRead(BaseModel):
    id: int = Field(..., description="Идентификатор пользователя")
    name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    role: SUserRole = Field(..., description="Роль пользователя")
    new_mes_count: int = 0
    is_online: bool | None = None

    model_config = ConfigDict(from_attributes=True)

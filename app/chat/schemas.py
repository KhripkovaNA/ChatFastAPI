from pydantic import BaseModel, Field


class SMessageCreate(BaseModel):
    recipient_id: int = Field(..., description="ID получателя сообщения")
    content: str = Field(..., description="Содержимое сообщения")


class SMessageAdd(SMessageCreate):
    sender_id: int = Field(..., description="ID отправителя сообщения")


class SMessageRead(SMessageAdd):
    id: int = Field(..., description="Уникальный идентификатор сообщения")




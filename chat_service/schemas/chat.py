import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# --- Кімнати (Rooms) ---

class RoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Загальний чат")

class RoomCreate(RoomBase):
    """Схема для створення кімнати (тільки назва)"""
    pass

class RoomRead(RoomBase):
    """Схема для відображення кімнати"""
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Повідомлення (Messages) ---

class MessageBase(BaseModel):
    text: str = Field(..., min_length=1, example="Привіт усім!")

class MessageCreate(MessageBase):
    text: str

class MessageRead(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    sender_id: uuid.UUID
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Учасники (Members) ---

class MemberAdd(BaseModel):
    """Схема для додавання користувача в чат"""
    user_id: uuid.UUID

class MemberRead(BaseModel):
    """Схема для списку учасників"""
    user_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)
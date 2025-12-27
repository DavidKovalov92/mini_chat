import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


class UserRead(BaseModel):
    id: uuid.UUID
    username: str
    first_name: str | None
    last_name: str | None
    bio: str | None
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_seen_at: datetime | None


    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
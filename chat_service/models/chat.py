import uuid
from datetime import datetime
from typing import List
from sqlalchemy import String, ForeignKey, Text, DateTime, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

# Таблиця-зв'язка для учасників чату (Many-to-Many)
chat_members = Table(
    "chat_members",
    Base.metadata,
    Column("room_id", ForeignKey("chat_rooms.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", UUID(as_uuid=True), primary_key=True), # UUID юзера з іншого сервісу
)

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Зв'язки
    messages: Mapped[List["Message"]] = relationship(back_populates="room", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Зв'язок з кімнатою
    room: Mapped["ChatRoom"] = relationship(back_populates="messages")
import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class AuthUser(Base):
    __tablename__ = "authusers"

    # 'id' ПЕРЕОПРЕДЕЛЯЕТ 'id' из Base
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True
    )

    email: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"AuthUser(id={self.id!r}, email={self.email!r})"
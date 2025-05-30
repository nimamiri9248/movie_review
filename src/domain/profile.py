import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.db import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'), unique=True, nullable=False)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")
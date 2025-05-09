from sqlalchemy import ForeignKey, Text, UniqueConstraint, Integer, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from src.core.db import Base
import uuid


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint('user_id', 'film_id', name='user_film_uc'),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    film_id: Mapped[int] = mapped_column(Integer, ForeignKey('films.id', ondelete='CASCADE'), nullable=False)
    rating: Mapped[float] = mapped_column(CheckConstraint('rating >= 0 AND rating <= 5'), nullable=False)
    review_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="reviews", passive_deletes=True)
    film: Mapped["Film"] = relationship("Film", back_populates="reviews")
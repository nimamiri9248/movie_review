from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.core.db import Base
import uuid


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint('user_id', 'film_id', name='user_film_uc'),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    film_id: Mapped[int] = mapped_column(ForeignKey("films.id"), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    review_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="reviews")
    film: Mapped["Film"] = relationship("Film", back_populates="reviews")
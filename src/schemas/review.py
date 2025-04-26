import uuid

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ReviewCreate(BaseModel):
    film_id: int
    rating: int
    review_text: str | None = None


class ReviewResponse(BaseModel):
    id: int
    user_id: uuid.UUID
    film_id: int
    rating: int
    review_text: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

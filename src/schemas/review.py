import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Annotated


class ReviewCreate(BaseModel):
    film_id: int
    rating: Annotated[int, Field(ge=0, le=5, description="Rating must be between 1 and 10")]
    review_text: Annotated[str, Field(max_length=5000)] | None = Field(
        default=None, description="Optional review text, max 5000 characters"
    )


class ReviewResponse(BaseModel):
    id: int
    user_id: uuid.UUID | None
    film_id: int
    rating: int
    review_text: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

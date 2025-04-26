import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth import User
from src.persistence.dependencies import get_current_user
from src.services.review import list_reviews_for_film, list_reviews_by_user, upsert_review
from src.schemas.review import ReviewCreate, ReviewResponse
from src.core.db import get_db

router = APIRouter()


@router.post("/reviews", response_model=ReviewResponse)
async def upsert_review_route(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review_obj = await upsert_review(
        db, current_user.id, review.film_id, review.rating, review.review_text
    )
    return review_obj


@router.get("/films/{film_id}/reviews", response_model=list[ReviewResponse])
async def get_reviews_for_film(
    film_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await list_reviews_for_film(db, film_id)


@router.get("/users/{user_id}/reviews", response_model=list[ReviewResponse])
async def get_reviews_by_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    return await list_reviews_by_user(db, user_id)

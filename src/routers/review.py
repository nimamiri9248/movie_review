import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.common import ResponseModel
from src.domain.auth import User
from src.persistence.dependencies import get_current_user
import src.services.review as  service
from src.schemas.review import ReviewCreate, ReviewResponse
from src.core.db import get_db

router = APIRouter()


@router.post("/reviews", response_model=ResponseModel[ReviewResponse], status_code=status.HTTP_201_CREATED)
async def upsert_review_route(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = await service.upsert_review(
        db, current_user.id, review.film_id, review.rating, review.review_text
    )
    return ResponseModel(msg="review retrieved", result=review)


@router.get("/films/{film_id}/reviews", response_model=ResponseModel[list[ReviewResponse]],
            status_code=status.HTTP_200_OK)
async def get_reviews_for_film(
    film_id: int,
    db: AsyncSession = Depends(get_db)
):
    reviews = await service.list_reviews_for_film(db, film_id)
    return ResponseModel(msg="reviews retrieved", result=reviews)


@router.get("/users/{user_id}/reviews", response_model=ResponseModel[list[ReviewResponse]],
            status_code=status.HTTP_200_OK)
async def get_reviews_by_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    reviews = await service.list_reviews_by_user(db, user_id)
    return ResponseModel(msg="reviews retrieved", result=reviews)


@router.get("review/{review_id}", response_model=ResponseModel[ReviewResponse], status_code=status.HTTP_200_OK)
async def get_review(review_id: int,
                     db: AsyncSession = Depends(get_db)):
    review = await service.get_review(db, review_id)
    return ResponseModel(msg="review retrieved", result=review)

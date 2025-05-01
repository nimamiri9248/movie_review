import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth import User
from src.domain.review import Review
import src.persistence.review as persistence
from src.persistence.helper_funcs import update_film_rating


async def upsert_review(
    db: AsyncSession, user_id: uuid.UUID, film_id: int, rating: int, review_text: str | None
) -> Review:
    existing_review = await persistence.get_review_by_user_and_film(db, user_id, film_id)

    if existing_review:
        review = await persistence.update_review(db, existing_review, rating, review_text)
    else:
        review = await persistence.create_review(db, user_id, film_id, rating, review_text)
    await update_film_rating(db, review.film_id)
    return review


async def list_reviews_for_film(db: AsyncSession, film_id: int) -> list[Review]:
    return await persistence.get_reviews_by_film(db, film_id)


async def list_reviews_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[Review]:
    return await persistence.get_reviews_by_user(db, user_id)


async def get_review(db: AsyncSession, review_id: int) -> Review:
    return await persistence.get_review_by_id(db, review_id)


async def delete_review_service(db: AsyncSession, review_id: int, current_user: User) -> None:
    review = await persistence.get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")
    await persistence.delete_review(db, review)
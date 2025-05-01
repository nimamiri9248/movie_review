import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.review import Review
import src.persistence.review as persistence


async def upsert_review(
    db: AsyncSession, user_id: uuid.UUID, film_id: int, rating: int, review_text: str | None
) -> Review:
    existing_review = await persistence.get_review_by_user_and_film(db, user_id, film_id)

    if existing_review:
        return await persistence.update_review(db, existing_review, rating, review_text)
    else:
        return await persistence.create_review(db, user_id, film_id, rating, review_text)


async def list_reviews_for_film(db: AsyncSession, film_id: int) -> list[Review]:
    return await persistence.get_reviews_by_film(db, film_id)


async def list_reviews_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[Review]:
    return await persistence.get_reviews_by_user(db, user_id)


async def get_review(db: AsyncSession, review_id: int) -> Review:
    return await persistence.get_review(db, review_id)
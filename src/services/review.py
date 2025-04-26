import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.review import Review
from src.persistence.review import create_review, get_reviews_by_film, get_reviews_by_user, get_review_by_user_and_film, \
    update_review


async def upsert_review(
    db: AsyncSession, user_id: UUID, film_id: int, rating: int, review_text: str | None
) -> Review:
    existing_review = await get_review_by_user_and_film(db, user_id, film_id)

    if existing_review:
        return await update_review(db, existing_review, rating, review_text)
    else:
        return await create_review(db, user_id, film_id, rating, review_text)


async def list_reviews_for_film(db: AsyncSession, film_id: int) -> list[Review]:
    return await get_reviews_by_film(db, film_id)


async def list_reviews_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[Review]:
    return await get_reviews_by_user(db, user_id)

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.domain.review import Review


async def create_review(db: AsyncSession, user_id: uuid.UUID, film_id: int, rating: int, review_text: str | None) -> Review:
    review = Review(user_id=user_id, film_id=film_id, rating=rating, review_text=review_text)
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def update_review(db: AsyncSession, review: Review, rating: int, review_text: str | None) -> Review:
    review.rating = rating
    review.review_text = review_text
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def get_review_by_user_and_film(db: AsyncSession, user_id: uuid.UUID, film_id: int) -> Review | None:
    result = await db.execute(
        select(Review).where(Review.user_id == user_id, Review.film_id == film_id)
    )
    return result.scalars().first()


async def get_reviews_by_film(db: AsyncSession, film_id: int) -> list[Review]:
    result = await db.execute(select(Review).filter(Review.film_id == film_id).options(selectinload(Review.user)))
    return list(result.scalars().all())


async def get_reviews_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[Review]:
    result = await db.execute(select(Review).filter(Review.user_id == user_id).options(selectinload(Review.film)))
    return list(result.scalars().all())

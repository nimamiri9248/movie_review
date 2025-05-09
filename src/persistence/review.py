import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.domain.review import Review


async def create_review(db: AsyncSession, user_id: uuid.UUID, film_id: int, rating: int,
                        review_text: str | None, commit: bool = False) -> Review:
    review = Review(user_id=user_id, film_id=film_id, rating=rating, review_text=review_text)
    db.add(review)
    await db.flush()
    if commit:
        await db.commit()
    await db.refresh(review)
    return review


async def update_review(db: AsyncSession, review: Review, rating: int, review_text: str | None,
                        commit: bool = False) -> Review:
    review.rating = rating
    review.review_text = review_text
    db.add(review)
    await db.flush()
    await db.refresh(review)
    if commit:
        await db.commit()
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


async def get_review_by_id(db: AsyncSession, review_id: int) -> Review:
    result = await db.execute(select(Review).filter(Review.id == review_id).options(selectinload(Review.film)))
    return result.scalars().first()


async def delete_review(db: AsyncSession, review: Review) -> None:
    await db.delete(review)
    await db.commit()


async def get_user_liked_film_ids(
    db: AsyncSession, user_id: uuid.UUID, min_rating: float = 3.0
) -> list[str]:
    """
    Return list of film IDs that the user rated >= min_rating.
    """
    result = await db.execute(
        select(Review.film_id)
        .where(Review.user_id == user_id)
        .where(Review.rating >= min_rating)
    )
    return [str(row[0]) for row in result.all()]


async def get_user_seen_film_ids(
    db: AsyncSession, user_id: uuid.UUID
) -> set[str]:
    """
    Return set of all film IDs that the user has rated at all.
    """
    result = await db.execute(
        select(Review.film_id)
        .where(Review.user_id == user_id)
    )
    return {str(row[0]) for row in result.all()}
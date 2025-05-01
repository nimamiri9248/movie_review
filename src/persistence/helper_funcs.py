from sqlalchemy import  select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.film import Film


async def update_film_rating(db: AsyncSession, film_id: int) -> None:
    async with db.begin():
        film = await db.execute(
            select(Film)
            .options(selectinload(Film.reviews))
            .where(Film.id == film_id)
            .with_for_update()
        )
        film = film.scalar_one()

        avg_rating = (
            sum(review.rating for review in film.reviews) / len(film.reviews)
            if film.reviews else None
        )
        review_count = len(film.reviews)

        film.rating = avg_rating
        film.review_count = review_count

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.domain.film import Film, Genre


async def create_film(db: AsyncSession, film: Film) -> Film:
    db.add(film)
    await db.commit()
    await db.refresh(film)
    return film


async def get_film_by_id(db: AsyncSession, film_id: int) -> Film | None:
    result = await db.execute(
        select(Film).where(Film.id == film_id).options(selectinload(Film.genres))
    )
    return result.scalars().first()


async def update_film(db: AsyncSession, film: Film) -> Film:
    await db.commit()
    await db.refresh(film)
    return film


async def get_films(db: AsyncSession, filters: dict) -> list[Film]:
    query = select(Film).options(selectinload(Film.genres))
    if "genre_id" in filters:
        query = query.join(Film.genres).filter(Genre.id == filters["genre_id"])
    if "director" in filters:
        query = query.filter(Film.director.ilike(f"%{filters['director']}%"))
    if "release_year" in filters:
        query = query.filter(Film.release_year == filters["release_year"])

    result = await db.execute(query)
    return result.scalars().all()


async def get_genres_by_ids(db: AsyncSession, genre_ids: list[int]) -> list[Genre]:
    result = await db.execute(select(Genre).where(Genre.id.in_(genre_ids)))
    return result.scalars().all()

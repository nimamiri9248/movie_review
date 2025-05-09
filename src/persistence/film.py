from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.domain.film import Film, Genre


async def create_film(db: AsyncSession, film: Film, commit: bool = False) -> Film:
    db.add(film)
    await db.flush()
    await db.refresh(film)
    if commit:
        await db.commit()
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


async def get_films(
    db: AsyncSession,
    filters: dict = None,
    sort_by: str = None,
    sort_order: str = 'asc'
) -> list[Film]:
    query = select(Film).options(selectinload(Film.genres))

    filter_mappings = {
        "genre_id": lambda v: Film.genres.any(Genre.id == v),
        "director": lambda v: Film.director.ilike(f"%{v}%"),
        "release_year": lambda v: Film.release_year == v,
        "min_rating": lambda v: Film.rating >= v,
        "max_rating": lambda v: Film.rating <= v,
        "min_review_count": lambda v: Film.review_count >= v,
        "max_review_count": lambda v: Film.review_count <= v,
        "min_film_length": lambda v: Film.film_length >= v,
        "max_film_length": lambda v: Film.film_length <= v,
    }

    if filters:
        for key, value in filters.items():
            if value is None:
                continue  # skip null values
            condition = filter_mappings.get(key)
            if condition:
                query = query.filter(condition(value))

    allowed_sort_columns = {
        "release_year": Film.release_year,
        "film_length": Film.film_length,
        "rating": Film.rating,
        "review_count": Film.review_count,
        "director": Film.director,
    }

    sort_column = allowed_sort_columns.get(sort_by)
    if sort_column is not None:
        sort_column = sort_column.desc() if sort_order == 'desc' else sort_column.asc()
        query = query.order_by(sort_column)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_genres_by_ids(db: AsyncSession, genre_ids: list[int]) -> list[Genre]:
    result = await db.execute(select(Genre).where(Genre.id.in_(genre_ids)))
    return list(result.scalars().all())


async def delete_film(db: AsyncSession, film: Film) -> None:
    await db.delete(film)
    await db.commit()


async def get_films_by_ids(db: AsyncSession, film_ids: list) -> list[Film]:
    film_ids = [int(fid) for fid in film_ids if fid.isdigit()]
    result = await db.execute(select(Film).options(selectinload(Film.genres)).where(Film.id.in_(film_ids)))
    return list(result.scalars().all())
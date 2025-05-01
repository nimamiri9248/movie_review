from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence import film as persistence
from src.domain.film import Film
from src.persistence.film import get_genres_by_ids
from src.schemas.film import FilmCreateSchema, FilmUpdateSchema
from fastapi import HTTPException


async def create_film_service(db: AsyncSession, film_data: FilmCreateSchema) -> Film:
    genre_objs = await get_genres_by_ids(db, film_data.genre_ids)
    if len(genre_objs) != len(film_data.genre_ids):
        raise HTTPException(status_code=400, detail="Some genres not found")

    film = Film(
        title=film_data.title,
        director=film_data.director,
        release_year=film_data.release_year,
        description=film_data.description,
        poster_url=film_data.poster_url,
        genres=genre_objs
    )
    return await persistence.create_film(db, film)


async def update_film_service(db: AsyncSession, film_id: int, film_update: FilmUpdateSchema) -> Film:
    film = await persistence.get_film_by_id(db, film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")

    update_data = film_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(film, key, value)

    if film_update.genre_ids:
        genre_objs = await get_genres_by_ids(db, film_update.genre_ids)
        film.genres = genre_objs

    return await persistence.update_film(db, film)


async def list_films_service(db: AsyncSession, filters: dict) -> list[Film]:
    return await persistence.get_films(db, filters)


async def get_film_service(db: AsyncSession, film_id: int) -> Film:
    film = await persistence.get_film_by_id(db, film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film


async def delete_film(db: AsyncSession, film_id: int) -> None:
    film = await persistence.get_film_by_id(db, film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    await persistence.delete_film(db, film)

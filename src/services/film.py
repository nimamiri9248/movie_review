import uuid
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence import film as persistence
from src.domain.film import Film
from src.persistence.film import get_genres_by_ids, get_films_by_ids
from src.persistence.review import get_user_liked_film_ids, get_user_seen_film_ids
from src.schemas.film import FilmCreateSchema, FilmUpdateSchema
from fastapi import HTTPException
from src.services import recommender


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
        genres=genre_objs,
        film_length=film_data.film_length
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


async def list_films_service(db: AsyncSession, filters: dict, sort_by: str, sort_order: str) -> list[Film]:
    return await persistence.get_films(db, filters,sort_by, sort_order)


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


async def get_similar_movies(db: AsyncSession, title: str, top_n: int):
    film_ids = recommender.get_similar_movies(title, top_n)
    return await persistence.get_films_by_ids(db, film_ids)


async def recommend_by_content_for_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    min_rating: float = 3.0,
    top_n: int = 10,
    per_movie_similar: int = 5
) -> list[str]:
    liked_ids = await get_user_liked_film_ids(db, user_id, min_rating)
    print(liked_ids)
    if not liked_ids:
        return []
    candidates = []
    for fid in liked_ids:
        sims = recommender.get_similar_movies(fid, top_n=per_movie_similar)
        candidates.extend(sims)

    # 3) Which films has the user already seen?
    seen_ids = await get_user_seen_film_ids(db, user_id)

    # 4) Rank by frequency, excluding seen films
    freq = Counter([c for c in candidates if c not in seen_ids])
    top_ids = [fid for fid, _ in freq.most_common(top_n)]
    return top_ids


async def recommend_films_for_user_content(
    db: AsyncSession, user_id: uuid.UUID, **kwargs
) -> list[Film]:
    """
    Convenience wrapper that returns Film objects.
    """
    top_ids = await recommend_by_content_for_user(db, user_id, **kwargs)
    if not top_ids:
        return []
    return await get_films_by_ids(db, top_ids)

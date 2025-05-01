from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.dependencies import require_role
import src.services.film as service
from src.schemas.film import (
    FilmCreateSchema,
    FilmUpdateSchema,
    FilmResponseSchema
)
from src.schemas.common import ResponseModel
from src.core.db import get_db
from src.domain.auth import User

router = APIRouter()


@router.post("/films", response_model=ResponseModel[FilmResponseSchema])
async def add_film(
    film_data: FilmCreateSchema,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
):
    film = await service.create_film_service(db, film_data)
    return ResponseModel(msg="Film added", result=film)


@router.patch("/films/{film_id}", response_model=ResponseModel[FilmResponseSchema])
async def update_film(
    film_id: int,
    film_update: FilmUpdateSchema,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
):
    film = await service.update_film_service(db, film_id, film_update)
    return ResponseModel(msg="Film updated", result=film)


@router.get("/films", response_model=ResponseModel[list[FilmResponseSchema]])
async def list_films(
    genre_id: int | None = Query(default=None),
    director: str | None = Query(default=None),
    release_year: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    filters = {}
    if genre_id is not None:
        filters["genre_id"] = genre_id
    if director is not None:
        filters["director"] = director
    if release_year is not None:
        filters["release_year"] = release_year

    films = await service.list_films_service(db, filters)
    return ResponseModel(msg="Films retrieved", result=films)


@router.get("/films/{film_id}", response_model=ResponseModel[FilmResponseSchema])
async def get_film(
    film_id: int,
    db: AsyncSession = Depends(get_db)
):
    film = await service.get_film_service(db, film_id)
    return ResponseModel(msg="Film retrieved", result=film)

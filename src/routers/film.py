from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.dependencies import require_role, get_current_user
import src.services.film as service
from src.schemas.film import (
    FilmCreateSchema,
    FilmUpdateSchema,
    FilmResponseSchema, FilmQueryParams
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
    query: FilmQueryParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    filters = {k: v for k, v in query.dict().items()
               if k not in {"sort_by", "sort_order"} and v is not None}

    films = await service.list_films_service(db, filters, query.sort_by, query.sort_order)
    return ResponseModel(msg="Films retrieved", result=films)


@router.get("/films/{film_id}", response_model=ResponseModel[FilmResponseSchema])
async def get_film(
    film_id: int,
    db: AsyncSession = Depends(get_db)
):
    film = await service.get_film_service(db, film_id)
    return ResponseModel(msg="Film retrieved", result=film)


@router.delete("/films/{film_id}", response_model=ResponseModel[None])
async def delete_film(
    film_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
):
    await service.delete_film(db, film_id)
    return ResponseModel(msg="Film deleted", result=None)


@router.get(
    "/similar/{title}",
    response_model=ResponseModel[list[FilmResponseSchema]],
    summary="Content-based: movies similar to a given title",
)
async def similar_movies(
    title: str,
    top_n: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    films = await service.get_similar_movies(db, title, top_n)
    return ResponseModel(msg="", result=films)


@router.get(
    "/user-content",
    response_model=ResponseModel[list[FilmResponseSchema]],
    summary="Content-based recommendations for a user"
)
async def user_content_recs(
    top_n: int = Query(10, ge=1, le=50),
    per_movie_similar: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    films = await service.recommend_films_for_user_content(
        db, current_user.id, top_n=top_n, per_movie_similar=per_movie_similar
    )
    return ResponseModel(msg="", result=films)

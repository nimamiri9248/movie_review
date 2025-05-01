from pydantic import BaseModel, ConfigDict
from typing import Annotated
from pydantic import Field


class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class FilmCreateSchema(BaseModel):
    title: str
    director: str
    release_year: int
    description: str | None = None
    poster_url: str | None = None
    genre_ids: Annotated[list[int], Field(min_length=1)]


class FilmUpdateSchema(BaseModel):
    title: str | None = None
    director: str | None = None
    release_year: int | None = None
    description: str | None = None
    poster_url: str | None = None
    genre_ids: list[int] | None = None


class FilmResponseSchema(BaseModel):
    id: int
    title: str
    director: str
    release_year: int
    description: str | None = None
    poster_url: str | None = None
    genres: list[GenreSchema]
    rating: float
    review_count: int
    model_config = ConfigDict(from_attributes=True)


class FilmFilterSchema(BaseModel):
    genre_id: int | None = None
    director: str | None = None
    release_year: int | None = None
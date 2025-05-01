from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated


class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class FilmCreateSchema(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=200)]
    director: Annotated[str, Field(min_length=1, max_length=100)]
    release_year: Annotated[int, Field(ge=1888, description="Earliest known film year is 1888")]
    description: str | None = None
    poster_url: str | None = None
    film_length: Annotated[int, Field(ge=1, description="Length in minutes")]
    genre_ids: Annotated[list[int], Field(min_length=1)]


class FilmUpdateSchema(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=200)] | None = None
    director: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    release_year: Annotated[int, Field(1888)] | None = None
    description: str | None = None
    poster_url: str | None = None
    genre_ids: list[int] | None = None
    film_length: Annotated[int, Field(ge=1)] | None = None


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
    film_length: int

    model_config = ConfigDict(from_attributes=True)


class FilmFilterSchema(BaseModel):
    genre_id: int | None = None
    director: str | None = None
    release_year: int | None = None


class FilmQueryParams(BaseModel):
    genre_id: int | None = None
    director: str | None = None
    release_year: int | None = None
    min_rating: Annotated[float, Field(ge=0, le=10)] | None = None
    max_rating: Annotated[float, Field(ge=0, le=10)] | None = None
    min_review_count: Annotated[int, Field(ge=0)] | None = None
    max_review_count: Annotated[int, Field(ge=0)] | None = None
    min_film_length: Annotated[int, Field(ge=1)] | None = None
    max_film_length: Annotated[int, Field(ge=1)] | None = None
    sort_by: Annotated[str, Field(description="Options: release_year, film_length, rating, review_count, director")] | None = None
    sort_order: Annotated[str, Field(description="Options: asc, desc")] = "asc"

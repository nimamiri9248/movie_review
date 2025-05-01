from sqlalchemy import Column, String, Integer, ForeignKey, Table, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.core.db import Base


film_genre_association = Table(
    'film_genre',
    Base.metadata,
    Column('film_id', ForeignKey('films.id'), primary_key=True),
    Column('genre_id', ForeignKey('genres.id'), primary_key=True)
)


class Genre(Base):
    __tablename__ = 'genres'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    films: Mapped[list["Film"]] = relationship(
        secondary=film_genre_association,
        back_populates="genres"
    )


class Film(Base):
    __tablename__ = 'films'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    director: Mapped[str] = mapped_column(nullable=False)
    release_year: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    poster_url: Mapped[str] = mapped_column(String, nullable=True)
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="film", cascade="all, delete-orphan")
    genres: Mapped[list[Genre]] = relationship(
        secondary=film_genre_association,
        back_populates="films"
    )
    rating: Mapped[float] = mapped_column(Float, nullable=True, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
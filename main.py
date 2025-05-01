from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.dependencies import init_roles, create_initial_admin
from src.core.config import settings
from src.routers import auth, film, review,  profile
from src.core.db import engine, Base


app = FastAPI(title=settings.project_name)

app.include_router(film.router, prefix="/movies", tags=["Films"])
app.include_router(review.router, prefix="/reviews", tags=["Reviews"])
app.include_router(profile.router, prefix="/profile", tags=["profiles"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        await init_roles(session)
        await create_initial_admin(session)
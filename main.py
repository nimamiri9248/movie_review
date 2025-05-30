from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.dependencies import init_roles, create_initial_admin
from src.core.config import settings
from src.routers import auth, film, review,  profile
from src.core.db import engine, Base
from src.services.recommender import load_recommendation_model

app = FastAPI(title=settings.project_name)

app.include_router(film.router, tags=["Films"])
app.include_router(review.router, tags=["Reviews"])
app.include_router(profile.router, tags=["profiles"])
app.include_router(auth.router, tags=["Auth"])


@app.on_event("startup")
async def on_startup():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        await init_roles(session)
        await create_initial_admin(session)
    load_recommendation_model()
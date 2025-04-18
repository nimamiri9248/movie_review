from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.dependencies import init_roles, create_initial_admin
from src.core.config import settings
# from src.routes import user, movie, review, series
from src.routers.auth import router as auth_router
from src.core.db import engine, Base, get_db

app = FastAPI(title=settings.project_name)

# app.include_router(user.router, prefix="/users", tags=["Users"])
# app.include_router(movie.router, prefix="/movies", tags=["Movies"])
# app.include_router(review.router, prefix="/reviews", tags=["Reviews"])
# app.include_router(series.router, prefix="/series", tags=["Series"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        await init_roles(session)
        await create_initial_admin(session)
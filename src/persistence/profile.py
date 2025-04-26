import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.domain.profile import UserProfile


async def create_user_profile(db: AsyncSession, user_id: uuid.UUID, bio: str | None, avatar_url: str | None) -> UserProfile:
    profile = UserProfile(user_id=user_id, bio=bio, avatar_url=avatar_url)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_user_profile(db: AsyncSession, user_id: uuid.UUID) -> UserProfile | None:
    result = await db.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    return result.scalars().first()


async def update_user_profile(db: AsyncSession, profile: UserProfile) -> None:
    db.add(profile)

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.persistence.profile as persistence
from src.domain.profile import UserProfile


async def create_or_update_user_profile(db: AsyncSession,
                                        user_id: uuid.UUID, bio: str | None, avatar_url: str | None) -> UserProfile:
    profile = await persistence.get_user_profile(db, user_id)
    if profile:
        profile.bio = bio
        profile.avatar_url = avatar_url

        return await persistence.update_user_profile(db, profile, commit=True)
    return await persistence.create_user_profile(db, user_id, bio, avatar_url, commit=True)


async def get_user_profile(db: AsyncSession, user_id: uuid.UUID) -> UserProfile:
    profile = await persistence.get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no such profile")
    return profile




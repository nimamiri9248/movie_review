import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from src.persistence.profile import create_user_profile, get_user_profile, update_user_profile
from src.domain.profile import UserProfile
from src.schemas.profile import UserProfileUpdate


async def create_or_update_user_profile(db: AsyncSession,
                                        user_id: uuid.UUID, bio: str | None, avatar_url: str | None) -> UserProfile:
    profile = await get_user_profile(db, user_id)
    if profile:
        profile.bio = bio
        profile.avatar_url = avatar_url
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile
    return await create_user_profile(db, user_id, bio, avatar_url)


async def update_user_profile_service(
    db: AsyncSession, user_id: uuid.UUID, profile_update: UserProfileUpdate
) -> UserProfile:
    profile = await get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    await update_user_profile(db, profile)
    await db.commit()
    await db.refresh(profile)
    return profile

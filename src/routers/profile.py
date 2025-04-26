from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth import User
from src.persistence.dependencies import get_current_user
from src.services.profile import create_or_update_user_profile
from src.schemas.profile import UserProfileCreate, UserProfileResponse
from src.core.db import get_db

router = APIRouter()


@router.post("/users/me/profile", response_model=UserProfileResponse)
async def create_or_update_profile(
    profile: UserProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_or_update_user_profile(db, current_user.id, profile.bio, profile.avatar_url)

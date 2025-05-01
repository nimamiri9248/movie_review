from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.domain.auth import User
from src.persistence.dependencies import get_current_user
import src.services.profile as service
from src.schemas.common import ResponseModel
from src.schemas.profile import UserProfileCreate, UserProfileResponse
from src.core.db import get_db

router = APIRouter()


@router.post("/users/me/profile", response_model=ResponseModel[UserProfileResponse], status_code=status.HTTP_201_CREATED)
async def create_or_update_profile(
    profile: UserProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = await service.create_or_update_user_profile(db, current_user.id, profile.bio, profile.avatar_url)
    return ResponseModel(msg="it was done succussfully", result=profile)


@router.get("/users/me/profile", response_model=ResponseModel[UserProfileResponse], status_code=status.HTTP_200_OK)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = await service.get_user_profile(db, current_user.id)
    return ResponseModel(msg="profile was retrieved succussfully", result=profile)


@router.delete("/users/{user_id}/profile", response_model=ResponseModel[None], status_code=status.HTTP_200_OK)
async def deactivate_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await service.delete_user_profile(db, user_id, current_user)
    return ResponseModel(msg="Profile deactivated successfully", result=None)

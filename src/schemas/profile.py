import uuid

from pydantic import BaseModel, ConfigDict


class UserProfileCreate(BaseModel):
    bio: str | None = None
    avatar_url: str | None = None


class UserProfileResponse(BaseModel):
    id: int
    user_id: uuid.UUID
    bio: str | None = None
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    bio: str | None = None
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
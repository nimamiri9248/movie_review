
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class RoleSchema(BaseModel):
    id: UUID
    name: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    role: RoleSchema


class ResponseModel(BaseModel):
    msg: str
    result: object | None = None


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenData(BaseModel):
    user_id: str
    token: str
    created_at: datetime
    expires_at: datetime


class RefreshTokenRequest(BaseModel):
    token: str = Field(..., description="Refresh token to obtain a new access token")


class LogoutRequest(BaseModel):
    token: str = Field(..., description="Refresh token to revoke")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to send the reset code")


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    code: str = Field(..., description="Reset code sent to the user's email")
    new_password: str = Field(..., description="New password for the user")


class PromoteUserRequest(BaseModel):
    user_id: UUID


class RegisterAdminRequest(BaseModel):
    email: EmailStr
    password: str

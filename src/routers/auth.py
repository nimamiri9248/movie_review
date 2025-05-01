import uuid

from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.domain.auth import User
from src.persistence.dependencies import get_current_user, require_role
from src.schemas.auth import UserCreate, LoginSchema, UserResponse, ForgotPasswordRequest, LogoutRequest, \
    RefreshTokenRequest, ResetPasswordRequest, PromoteUserRequest, RegisterAdminRequest
from src.schemas.common import ResponseModel
import src.services.auth as service

router = APIRouter()


@router.post("/register", response_model=ResponseModel[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await service.register_user(db, user_data)
    return ResponseModel(msg="User registered successfully", result=user)


@router.post("/login", response_model=ResponseModel[dict])
async def login(login_data: LoginSchema, db: AsyncSession = Depends(get_db)):
    tokens = await service.authenticate_user(db, login_data)
    return ResponseModel(msg="Login successful", result=tokens)


@router.post("/refresh", response_model=ResponseModel[dict])
async def refresh(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    access_token = await service.refresh_access_token(request.token, db)
    return ResponseModel(msg="Access token refreshed", result={"access_token": access_token})


@router.post("/logout", response_model=ResponseModel[None])
async def logout(request: LogoutRequest):
    await service.revoke_refresh_token(request.token)
    return ResponseModel(msg="Logged out successfully")


@router.post("/forgot-password", response_model=ResponseModel[None])
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks,
                          db: AsyncSession = Depends(get_db)):
    await service.send_reset_code(db, request.email, background_tasks)
    return ResponseModel(msg="Reset code sent to email")


@router.post("/reset-password", response_model=ResponseModel[None])
async def reset_password_endpoint(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await service.reset_password(request.email, request.code, request.new_password, db)
    return ResponseModel(msg="Password updated successfully")


@router.get("/me", response_model=ResponseModel[UserResponse], status_code=status.HTTP_200_OK)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return ResponseModel(msg="User profile retrieved successfully", result=current_user)


@router.get("/users", response_model=ResponseModel[list[UserResponse]], status_code=status.HTTP_200_OK)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    users = await service.get_all_users(db)
    return ResponseModel(msg="All users retrieved successfully", result=users)


@router.get("/user/{user_id}", response_model=ResponseModel[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    user_id: uuid.UUID,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
):
    user = await service.get_user(db, user_id, include_inactive)
    return ResponseModel(msg="All user retrieved successfully", result=user)


@router.post("/admin/promote", response_model=ResponseModel[UserResponse])
async def promote_user(
    request: PromoteUserRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
):
    user = await service.promote_user_to_admin(db, request.user_id)
    return ResponseModel(msg="User promoted to admin", result=user)


@router.post("/admin/register", response_model=ResponseModel[UserResponse])
async def register_admin(
    request: RegisterAdminRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
):
    user = await service.register_admin_user(db, request.email, request.password)
    return ResponseModel(msg="Admin registered", result=user)


@router.delete("/me", response_model=ResponseModel[None], status_code=status.HTTP_200_OK)
async def delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await service.delete_own_account(db, current_user)
    return ResponseModel(msg="Account deleted successfully", result=None)


@router.delete("/users/{user_id}", response_model=ResponseModel[None], status_code=status.HTTP_200_OK)
async def delete_user_by_admin(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
):
    await service.delete_user_by_admin(db, user_id)
    return ResponseModel(msg="User deleted successfully", result=None)
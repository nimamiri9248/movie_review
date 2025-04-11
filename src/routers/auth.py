from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.domain.auth import User
from src.persistence.dependencies import get_current_user, require_role
from src.schemas.auth import UserCreate, LoginSchema, UserResponse, ForgotPasswordRequest, LogoutRequest, \
    RefreshTokenRequest, ResetPasswordRequest
from src.schemas.base_schema import ResponseModel
from src.services.auth import register_user, authenticate_user, refresh_access_token, revoke_refresh_token, \
    send_reset_code, reset_password

router = APIRouter()


@router.post("/register", response_model=ResponseModel[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, user_data)
    return ResponseModel(msg="User registered successfully", result=user)


@router.post("/login", response_model=ResponseModel[dict])
async def login(login_data: LoginSchema, db: AsyncSession = Depends(get_db)):
    tokens = await authenticate_user(db, login_data)
    return ResponseModel(msg="Login successful", result=tokens)


@router.post("/refresh", response_model=ResponseModel[dict])
async def refresh(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    access_token = await refresh_access_token(request.token, db)
    return ResponseModel(msg="Access token refreshed", result={"access_token": access_token})


@router.post("/logout", response_model=ResponseModel[None])
async def logout(request: LogoutRequest):
    await revoke_refresh_token(request.token)
    return ResponseModel(msg="Logged out successfully")


@router.post("/forgot-password", response_model=ResponseModel[None])
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    await send_reset_code(request.email, background_tasks)
    return ResponseModel(msg="Reset code sent to email")


@router.post("/reset-password", response_model=ResponseModel[None])
async def reset_password_endpoint(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await reset_password(request.email, request.code, request.new_password, db)
    return ResponseModel(msg="Password updated successfully")


@router.get("/me", response_model=ResponseModel[UserResponse], status_code=status.HTTP_200_OK)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return ResponseModel(msg="User profile retrieved successfully", result=current_user)


@router.get("/users", response_model=ResponseModel[list[UserResponse]], status_code=status.HTTP_200_OK)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    users = await get_all_users(db)
    return ResponseModel(msg="All users retrieved successfully", result=users)

import uuid
from datetime import datetime, timedelta,UTC
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, BackgroundTasks
from src.persistence import auth as persistence
from src.utils import hashing, jwt
from src.domain.auth import User
from src.schemas.auth import UserCreate, LoginSchema, TokenData
from src.core.redis import get_redis_client
from src.utils.email import send_email


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    existing_user = await persistence.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    role = await persistence.get_role_by_name(db, "user")
    if not role:
        raise HTTPException(status_code=400, detail="Role not found")

    hashed_password = hashing.hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        role_id=role.id
    )
    return await persistence.create_user(db, new_user)


async def authenticate_user(db: AsyncSession, login_data: LoginSchema) -> dict:
    user = await persistence.get_user_by_email(db, login_data.email)
    if not user or not hashing.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = jwt.create_access_token(data={"sub": str(user.id), "role": user.role.name})
    refresh_token = jwt.create_refresh_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


async def create_refresh_token(user_id: str) -> str:
    redis_client: Redis = await get_redis_client()
    token = str(uuid.uuid4())
    created_at = datetime.now(UTC)
    expires_at = created_at + timedelta(days=30)
    token_data = TokenData(user_id=user_id, token=token, created_at=created_at, expires_at=expires_at)
    await redis_client.set(f"refresh_token:{token}", token_data.json(), ex=2592000)
    return token


async def get_refresh_token(token: str) -> TokenData | None:
    redis_client: Redis = await get_redis_client()
    token_data_json = await redis_client.get(f"refresh_token:{token}")
    if token_data_json:
        return TokenData.parse_raw(token_data_json)
    return None


async def revoke_refresh_token(token: str) -> None:
    redis_client: Redis = await get_redis_client()
    await redis_client.delete(f"refresh_token:{token}")


async def refresh_access_token(token: str, db: AsyncSession) -> str:
    redis_client = await get_redis_client()
    token_data_json = await redis_client.get(f"refresh_token:{token}")
    if not token_data_json:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_data = TokenData.parse_raw(token_data_json)
    if token_data.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    user = await persistence.get_user_by_id(db, uuid.UUID(token_data.user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return jwt.create_access_token(data={"sub": str(user.id), "role": user.role.name})


async def send_reset_code(email: str, background_tasks: BackgroundTasks) -> None:
    redis_client = await get_redis_client()
    code = str(uuid.uuid4()).split('-')[0]
    await redis_client.set(f"reset_code:{email}", code, ex=600)

    subject = "Your Password Reset Code"
    body = f"Your password reset code is: {code}"

    background_tasks.add_task(send_email, to_email=email, subject=subject, body=body)


async def reset_password(email: str, code: str, new_password: str, db: AsyncSession) -> None:
    redis_client = await get_redis_client()
    saved_code = await redis_client.get(f"reset_code:{email}")
    if not saved_code or saved_code.decode() != code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset code")

    user = await persistence.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = hashing.hash_password(new_password)
    await persistence.update_user_password(db, user)


async def get_all_users(db: AsyncSession) -> list[User]:
    return await persistence.get_all_users(db)

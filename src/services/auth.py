import datetime
import uuid
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, BackgroundTasks

from src.core.config import settings
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
        id=uuid.uuid4(),
        email=user_data.email,
        password=hashed_password,
        role_id=role.id,
        is_active=True
    )
    return await persistence.create_user(db, new_user, load_role=True, commit=True)


async def authenticate_user(db: AsyncSession, login_data: LoginSchema) -> dict:
    user = await persistence.get_user_by_email(db, login_data.email)
    if not user or not hashing.verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = jwt.create_access_token(data={"sub": str(user.id), "role": user.role.name})
    refresh_token = jwt.create_refresh_token(data={"sub": str(user.id)})
    await set_refresh_token(refresh_token, str(user.id))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


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
    token = await get_refresh_token(token)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    user = await persistence.get_user_by_id(db, uuid.UUID(token.user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return jwt.create_access_token(data={"sub": str(user.id), "role": user.role.name})


async def set_refresh_token(token: str, user_id: str, ) -> None:
    redis_client: Redis = await get_redis_client()
    created_at = datetime.datetime.now(datetime.UTC)
    expires_at = created_at + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_data = TokenData(
        user_id=user_id,
        token=token,
        created_at=created_at,
        expires_at=expires_at
    )
    await redis_client.set(f"refresh_token:{token}", token_data.json(), ex=expires_at - created_at)


async def send_reset_code(db: AsyncSession, email: str, background_tasks: BackgroundTasks) -> None:
    user = await persistence.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    redis_client = await get_redis_client()
    code = str(uuid.uuid4()).split('-')[0]
    await redis_client.set(f"reset_code:{email}", code, ex=settings.reset_code_expire_time)

    subject = "Your Password Reset Code"
    body = f"Your password reset code is: {code}"

    background_tasks.add_task(send_email, to_email=email, subject=subject, body=body)


async def reset_password(email: str, code: str, new_password: str, db: AsyncSession) -> None:
    redis_client = await get_redis_client()
    saved_code = await redis_client.get(f"reset_code:{email}")
    if not saved_code or saved_code != code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset code")

    user = await persistence.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_hashed_password = hashing.hash_password(new_password)
    await persistence.update_user_password(db, user, new_hashed_password, commit=True)


async def get_all_users(db: AsyncSession) -> list[User]:
    return await persistence.get_all_users(db)


async def promote_user_to_admin(db: AsyncSession, user_id: uuid.UUID) -> User:
    user = await persistence.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    admin_role = await persistence.get_role_by_name(db, "admin")
    if not admin_role:
        raise HTTPException(status_code=500, detail="Admin role not found")
    await persistence.modify_user_role(db, user, admin_role.id)
    return user


async def register_admin_user(db: AsyncSession, email: str, password: str) -> User:
    existing_user = await persistence.get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    admin_role = await persistence.get_role_by_name(db, "admin")
    if not admin_role:
        raise HTTPException(status_code=500, detail="Admin role not found")

    new_user = User(
        email=email,
        password=hashing.hash_password(password),
        role_id=admin_role.id,
        is_active=True
    )
    created_user = await persistence.create_user(db, new_user, commit=True)
    return created_user



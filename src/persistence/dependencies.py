import uuid

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from src.core.config import settings
from src.persistence import auth as persistence
from src.core.db import get_db
from src.domain.auth import Role, User
from uuid import uuid4
from src.utils import jwt, hashing

security = HTTPBearer(auto_error=True)


async def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return credentials.credentials


async def init_roles(db: AsyncSession):
    existing_roles = await db.execute(select(Role).filter(Role.name.in_(["admin", "user"])))
    existing_roles = {role.name for role in existing_roles.scalars().all()}
    roles_to_create = []

    if "admin" not in existing_roles:
        roles_to_create.append(Role(id=uuid4(), name="admin"))
    if "user" not in existing_roles:
        roles_to_create.append(Role(id=uuid4(), name="user"))

    if roles_to_create:
        db.add_all(roles_to_create)
        await db.commit()


async def get_current_user(token: str = Depends(get_token), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode_token(token)
        user_id: uuid.UUID = uuid.UUID(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await persistence.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(allowed_roles: list[str]) -> callable:
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


async def create_initial_admin(db: AsyncSession):
    existing_admin = await persistence.get_user_by_email(db, settings.admin_email)
    if existing_admin:
        return

    admin_role = await persistence.get_role_by_name(db, "admin")
    if not admin_role:
        raise Exception("Admin role not found. Make sure roles are initialized.")

    admin_user = User(
        email=settings.admin_email,
        password=hashing.hash_password(settings.admin_password),
        role_id=admin_role.id,
        is_active=True,
    )

    await persistence.create_user(db, admin_user, commit=True)

import uuid

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status
from src.persistence import auth as persistence
from src.core.config import settings
from src.core.db import get_db
from src.domain.auth import Role, User
from uuid import uuid4

from src.utils import jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
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

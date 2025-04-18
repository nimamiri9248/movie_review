from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.domain.auth import User, Role


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.role)).filter(User.email == email)
    )
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.role)).filter(User.id == user_id)
    )
    return result.scalars().first()


async def create_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await db.refresh(user, attribute_names=["role"])
    return user


async def get_role_by_name(db: AsyncSession, role_name: str) -> Role | None:
    result = await db.execute(select(Role).filter(Role.name == role_name))
    return result.scalars().first()


async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User).options(selectinload(User.role))
    )
    return result.scalars().all()


async def update_user_password(db: AsyncSession, user: User) -> None:
    await db.commit()
    await db.refresh(user)

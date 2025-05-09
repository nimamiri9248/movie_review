import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.domain.auth import User, Role


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .filter(User.email == email, User.is_active == True)
    )
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: UUID, include_inactive: bool = False) -> User | None:
    query = select(User).options(selectinload(User.role)).filter(User.id == user_id)
    if not include_inactive:
        query = query.filter(User.is_active == True)
    result = await db.execute(query)
    return result.scalars().first()


async def create_user(db: AsyncSession, user: User, commit: bool = False, load_role: bool = False) -> User:
    db.add(user)
    await db.flush()
    await db.refresh(user)

    if load_role:
        await db.refresh(user, attribute_names=["role"])

    if commit:
        await db.commit()

    return user


async def get_role_by_name(db: AsyncSession, role_name: str) -> Role | None:
    result = await db.execute(select(Role).filter(Role.name == role_name))
    return result.scalars().first()


async def get_all_users(db: AsyncSession, include_inactive: bool = False) -> list[User]:
    query = select(User).options(selectinload(User.role))
    if not include_inactive:
        query = query.filter(User.is_active == True)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_user_password(db: AsyncSession, user: User, new_password: str, commit: bool = False) -> None:
    user.password = new_password
    if commit:
        await db.commit()
        await db.refresh(user)


async def modify_user_role(db: AsyncSession, user: User, role_id: uuid.UUID, commit: bool = False):
    user.role_id = role_id
    if commit:
        await db.commit()
        await db.refresh(user, attribute_names=["role"])


async def update_user(db: AsyncSession, user: User, commit: bool =  False) -> None:
    db.add(user)
    await db.flush()
    await db.refresh(user)
    if commit:
        await db.commit()


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.domain.auth import Role
from uuid import uuid4


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

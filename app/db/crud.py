from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.db import models


async def get_user_by_email(db: AsyncSession, *, email: str) -> Optional[models.User]:
    stmt = select(models.User).where(models.User.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, *, user_id: str) -> Optional[models.User]:
    stmt = select(models.User).where(models.User.id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    name: str,
    password: str,
) -> models.User:
    hashed_password = security.get_password_hash(password)
    user = models.User(email=email, name=name, password_hash=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, *, email: str, password: str) -> Optional[models.User]:
    user = await get_user_by_email(db, email=email)
    if not user:
        return None
    if not security.verify_password(password, user.password_hash):
        return None
    return user


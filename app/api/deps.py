from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.db import crud
from app.db.session import get_session

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncSession:
    async with get_session() as session:
        yield session


async def get_current_user(
    token: str = Depends(reusable_oauth2),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = security.decode_token(token)
        user_id: str | None = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = await crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


from datetime import timedelta

from fastapi import HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession


from app.core import security
from app.db import crud
from app.schemas import auth as auth_schemas
from app.schemas import user as user_schemas


async def register_user(
    db: AsyncSession,
    payload: auth_schemas.RegisterRequest,
) -> auth_schemas.AuthResponse:
    existing = await crud.get_user_by_email(db, email=payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = await crud.create_user(
        db,
        email=payload.email,
        name=payload.name,
        password=payload.password,
    )

    access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(subject=str(user.id), expires_delta=access_token_expires)

    return auth_schemas.AuthResponse(
        user=user_schemas.UserPublic.from_orm(user),
        token=token,
    )


# async def login_user(
#     db: AsyncSession,
#     payload: auth_schemas.LoginRequest,
# ) -> auth_schemas.AuthResponse:
#     user = await crud.authenticate_user(db, email=payload.email, password=payload.password)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

#     access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     token = security.create_access_token(subject=str(user.id), expires_delta=access_token_expires)

#     return auth_schemas.AuthResponse(
#         user=user_schemas.UserPublic.from_orm(user),
#         token=token,
#     )






async def login_user(
    response: Response,
    db: AsyncSession,
    payload: auth_schemas.LoginRequest,
) -> auth_schemas.AuthResponse:

    user = await crud.authenticate_user(
        db,
        email=payload.email,
        password=payload.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token_expires = timedelta(
        minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token = security.create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires
    )

    # ✅ Set cookie here
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # True in production (HTTPS)
        samesite="lax",
        max_age=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return auth_schemas.AuthResponse(
        user=user_schemas.UserPublic.from_orm(user),
        token=token,
    )


async def logout_user() -> None:
    # Stateless JWT: handled client-side.
    return None


async def get_current_user_info(current_user) -> user_schemas.UserPublic:
    return user_schemas.UserPublic.from_orm(current_user)


from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.controllers.v1 import auth_controller
from app.core.config import settings
from app.schemas import auth as auth_schemas
from app.schemas import user as user_schemas

router = APIRouter()


@router.post("/register", response_model=auth_schemas.AuthResponse, status_code=201)
async def register(
    payload: auth_schemas.RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(deps.get_db),
) -> auth_schemas.AuthResponse:
    auth = await auth_controller.register_user(db=db, payload=payload)
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=auth.token,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return auth


@router.post("/login", response_model=auth_schemas.AuthResponse)
async def login(
    payload: auth_schemas.LoginRequest,
    response: Response,
    db: AsyncSession = Depends(deps.get_db),
) -> auth_schemas.AuthResponse:
    auth = await auth_controller.login_user(db=db, payload=payload)
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=auth.token,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return auth


@router.post("/logout", status_code=204)
async def logout(response: Response) -> None:
    await auth_controller.logout_user()
    response.delete_cookie(key=settings.AUTH_COOKIE_NAME)
    return None


@router.get("/me", response_model=user_schemas.UserPublic)
async def get_me(
    current_user=Depends(deps.get_current_user),
) -> user_schemas.UserPublic:
    return await auth_controller.get_current_user_info(current_user=current_user)


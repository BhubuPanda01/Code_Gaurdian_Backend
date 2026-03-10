from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.controllers.v1 import auth_controller
from app.schemas import auth as auth_schemas
from app.schemas import user as user_schemas

router = APIRouter()


@router.post("/register", response_model=auth_schemas.AuthResponse, status_code=201)
async def register(
    payload: auth_schemas.RegisterRequest,
    db: AsyncSession = Depends(deps.get_db),
) -> auth_schemas.AuthResponse:
    return await auth_controller.register_user(db=db, payload=payload)


@router.post("/login", response_model=auth_schemas.AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(deps.get_db),
) -> auth_schemas.AuthResponse:
    return await auth_controller.login_user(db=db, form_data=form_data)


@router.post("/logout", status_code=204)
async def logout() -> None:
    await auth_controller.logout_user()
    return None


@router.get("/me", response_model=user_schemas.UserPublic)
async def get_me(
    current_user=Depends(deps.get_current_user),
) -> user_schemas.UserPublic:
    return await auth_controller.get_current_user_info(current_user=current_user)


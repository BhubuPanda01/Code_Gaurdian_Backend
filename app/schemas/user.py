from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserPublic(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


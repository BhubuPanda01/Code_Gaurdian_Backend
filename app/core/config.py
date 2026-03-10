from functools import lru_cache
from typing import Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General
    APP_NAME: str = "Code Guardian Backend"
    ENV: str = Field(default="dev")

    # Supabase Postgres connection string
    DATABASE_URL: AnyUrl

    # Auth / security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


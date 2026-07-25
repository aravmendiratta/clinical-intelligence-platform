# backend/app/core/config.py
"""Application configuration loader.

All configuration values are read from environment variables. The
module uses Pydantic's BaseSettings for type safety and default
handling.
"""

from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # JWT
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # FastAPI Users secret (used for password reset tokens, etc.)
    FASTAPI_USERS_SECRET: str = Field(..., env="FASTAPI_USERS_SECRET")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Export a singleton for easy import throughout the project
settings = Settings()

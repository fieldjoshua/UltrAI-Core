"""Configuration module for the application."""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List
import os

from .loader import load_environment_settings

# Load settings
settings = load_environment_settings()

# Export commonly used settings
DATABASE_URL = settings.DATABASE_URL
DOCUMENT_STORAGE_PATH = settings.DOCUMENT_STORAGE_PATH
ALLOWED_EXTENSIONS = settings.ALLOWED_EXTENSIONS
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
API_V1_PREFIX = settings.API_V1_PREFIX


class Config(BaseSettings):
    """Application configuration."""

    PROJECT_NAME: str = "Ultra"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Storage
    DOCUMENT_STORAGE_PATH: str = os.getenv(
        "DOCUMENT_STORAGE_PATH",
        str(Path(__file__).parent.parent / "storage" / "documents"),
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        case_sensitive = True
        env_file = ".env"


# Create config instance
config = Config()

__all__ = [
    "settings",
    "DATABASE_URL",
    "DOCUMENT_STORAGE_PATH",
    "ALLOWED_EXTENSIONS",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
    "API_V1_PREFIX",
]

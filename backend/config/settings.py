"""
Core configuration settings for the UltraAI system.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseSettings, Field, SecretStr
from pydantic.env_settings import SettingsSourceCallable

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


class Settings(BaseSettings):
    """Core application settings."""

    # Application
    APP_NAME: str = "UltraAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # API
    API_PREFIX: str = "/api/v1"
    API_TITLE: str = "UltraAI API"
    API_DESCRIPTION: str = "API for UltraAI LLM orchestration system"
    API_VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr("your-secret-key-here")
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite:///./ultraai.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10

    # LLM Integration
    DEFAULT_LLM_PROVIDER: str = "openai"
    LLM_API_KEYS: Dict[str, SecretStr] = Field(default_factory=dict)
    LLM_MODELS: Dict[str, str] = Field(default_factory=dict)

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE_URL: str = "redis://localhost:6379/1"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            """Customize settings sources."""
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


# Create settings instance
settings = Settings()

# Export settings
__all__ = ["settings"]

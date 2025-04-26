"""
Core configuration settings for the UltraAI system.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseSettings, Field, SecretStr
from pydantic.env_settings import SettingsSourceCallable
from pydantic_settings import BaseSettings as PydanticSettings

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


class Settings(PydanticSettings):
    """Base application settings."""

    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Database
    DATABASE_URL: str = Field(default="sqlite:///backend/database/ultra.db")

    # Document storage
    DOCUMENT_STORAGE_PATH: Path = Field(default=Path("backend/document_storage"))
    ALLOWED_EXTENSIONS: set[str] = Field(
        default={".txt", ".pdf", ".doc", ".docx", ".md"}
    )

    # JWT settings
    JWT_SECRET_KEY: str = Field(default="your-secret-key")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # API settings
    API_V1_PREFIX: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="UltraAI")
    VERSION: str = Field(default="1.0.0")

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: Optional[str] = Field(default="logs/ultra.log")

    # Application
    APP_NAME: str = "UltraAI"
    APP_VERSION: str = "1.0.0"

    # API
    API_TITLE: str = "UltraAI API"
    API_DESCRIPTION: str = "API for UltraAI LLM orchestration system"
    API_VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr("your-secret-key-here")
    )
    ALGORITHM: str = "HS256"

    # Database
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

    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True
        use_enum_values = True

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

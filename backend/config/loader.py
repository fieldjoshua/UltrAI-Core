"""
Configuration loader for environment-specific settings.
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    PORT: int = Field(default=8081)

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///backend/database/ultra.db",
        description="Database connection string",
    )
    POSTGRES_USER: str = Field(default="ultrauser")
    POSTGRES_PASSWORD: str = Field(default="ultrapassword")
    POSTGRES_DB: str = Field(default="ultra")

    # Document storage
    DOCUMENT_STORAGE_PATH: Path = Field(
        default=Path("backend/document_storage"),
        description="Path to store uploaded documents",
    )

    # File upload settings
    ALLOWED_EXTENSIONS: set[str] = Field(
        default={".txt", ".pdf", ".doc", ".docx", ".md"},
        description="Allowed file extensions for upload",
    )

    # JWT settings
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key", description="Secret key for JWT token generation"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256", description="Algorithm for JWT token generation"
    )

    # API settings
    API_V1_PREFIX: str = Field(default="/api/v1", description="API version 1 prefix")
    CORS_ORIGIN: str = Field(default="*")
    BACKEND_URL: str = Field(default="http://localhost:8081")
    VITE_API_URL: str = Field(default="http://localhost:8081")

    # LLM API Keys
    OPENAI_API_KEY: str = Field(default="your-openai-key-here")
    ANTHROPIC_API_KEY: str = Field(default="your-anthropic-key-here")
    GOOGLE_API_KEY: str = Field(default="your-google-key-here")
    MISTRAL_API_KEY: str = Field(default="your-mistral-key-here")
    DEEPSEEK_API_KEY: str = Field(default="your-deepseek-key-here")

    # Monitoring
    SENTRY_DSN: str = Field(default="your-sentry-dsn-here")
    REACT_APP_SENTRY_DSN: str = Field(default="your-sentry-dsn-here")
    SENTRY_ENVIRONMENT: str = Field(default="development")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=1.0)

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: Optional[str] = Field(default="logs/ultra.log")

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


def load_environment_settings() -> Settings:
    """Load environment settings."""
    return Settings()


# Create settings instance
settings = load_environment_settings()

# Export settings
__all__ = ["settings", "Settings", "load_environment_settings"]

"""
Configuration loader for environment-specific settings.
"""

import os
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseSettings, Field

from .settings import Settings


class EnvironmentSettings(BaseSettings):
    """Environment-specific settings."""

    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./ultraai_dev.db")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Logging
    LOG_LEVEL: str = Field(default="DEBUG")
    LOG_FILE: Optional[str] = Field(default="ultraai_dev.log")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def load_environment_settings() -> Dict:
    """Load environment-specific settings."""
    env = os.getenv("ENVIRONMENT", "development")
    env_settings = EnvironmentSettings()

    # Override base settings with environment-specific settings
    settings_dict = Settings().dict()
    settings_dict.update(env_settings.dict())

    return settings_dict


# Create environment-specific settings instance
env_settings = EnvironmentSettings()

# Export settings
__all__ = ["env_settings", "load_environment_settings"]

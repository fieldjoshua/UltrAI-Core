"""
Application configuration settings.
"""

import os


class Config:
    """Application configuration class."""

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT != "production"

    # API Settings
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Feature Flags
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "true").lower() == "true"
    ENABLE_RATE_LIMIT = os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true"

    # Mock Mode
    USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
    MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

    # LLM Provider Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

    # Default Model Settings
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories for the application."""
        os.makedirs("logs", exist_ok=True)

    @classmethod
    def validate_configuration(cls) -> None:
        """Validate the application configuration."""
        # Add validation logic here
        pass

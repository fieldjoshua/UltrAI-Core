import os
from pathlib import Path


class Config:
    """Configuration settings for the application."""

    # Environment
    ENV = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENV == "development"

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ultra.db")

    # File storage
    UPLOAD_DIR = Path("uploads")
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".txt", ".pdf", ".doc", ".docx"}

    # Security
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 20

    # LLM settings
    USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

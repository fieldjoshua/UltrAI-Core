import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger("config")

# Determine environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
TESTING = os.getenv("TESTING", "false").lower() == "true"

# Load appropriate .env file based on environment
# Go up one level to get to project root (from app to root)
base_path = Path(os.path.dirname(__file__)).parent
env_files = [
    base_path / f".env.{ENVIRONMENT}.local",  # Environment-specific local overrides
    base_path / f".env.{ENVIRONMENT}",  # Environment-specific defaults
    base_path / ".env.local",  # Local overrides
    base_path / ".env",  # Default .env file
]

# Load the first env file that exists
for env_file in env_files:
    if env_file.exists():
        logger.info(f"Loading environment from {env_file}")
        load_dotenv(dotenv_path=str(env_file))
        break


class ConfigValidationError(Exception):
    """Exception raised for configuration validation errors."""

    pass


class Config:
    """Configuration object to hold runtime settings"""

    # Basic configuration
    ENVIRONMENT = ENVIRONMENT
    TESTING = TESTING
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    # In production (Render), use PORT; otherwise use API_PORT
    API_PORT = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Application paths
    BASE_PATH = str(base_path)
    DOCUMENT_STORAGE_PATH = os.getenv("DOCUMENT_STORAGE_PATH", "document_storage")
    TEMP_UPLOADS_PATH = os.getenv("TEMP_UPLOADS_PATH", "temp_uploads")
    TEMP_PATH = os.getenv("TEMP_PATH", "temp")
    LOGS_PATH = os.getenv("LOGS_PATH", "logs")

    # Convert relative paths to absolute paths
    if not os.path.isabs(DOCUMENT_STORAGE_PATH):
        DOCUMENT_STORAGE_PATH = os.path.join(BASE_PATH, DOCUMENT_STORAGE_PATH)
    if not os.path.isabs(TEMP_UPLOADS_PATH):
        TEMP_UPLOADS_PATH = os.path.join(BASE_PATH, TEMP_UPLOADS_PATH)
    if not os.path.isabs(TEMP_PATH):
        TEMP_PATH = os.path.join(BASE_PATH, TEMP_PATH)
    if not os.path.isabs(LOGS_PATH):
        LOGS_PATH = os.path.join(BASE_PATH, LOGS_PATH)

    # Mock configuration
    USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
    MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

    # LLM Configuration
    USE_MODEL_RUNNER = os.getenv("USE_MODEL_RUNNER", "false").lower() == "true"
    MODEL_RUNNER_TYPE = os.getenv("MODEL_RUNNER_TYPE", "cli")  # 'api' or 'cli'
    MODEL_RUNNER_URL = os.getenv("MODEL_RUNNER_URL", "http://localhost:8080")
    DEFAULT_LOCAL_MODEL = os.getenv("DEFAULT_LOCAL_MODEL", "ai/smollm2")
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")

    # Timeout Settings (in seconds)
    ORCHESTRATION_TIMEOUT = int(os.getenv("ORCHESTRATION_TIMEOUT", "90"))
    INITIAL_RESPONSE_TIMEOUT = int(os.getenv("INITIAL_RESPONSE_TIMEOUT", "60"))
    PEER_REVIEW_TIMEOUT = int(os.getenv("PEER_REVIEW_TIMEOUT", "90"))
    ULTRA_SYNTHESIS_TIMEOUT = int(os.getenv("ULTRA_SYNTHESIS_TIMEOUT", "60"))
    LLM_REQUEST_TIMEOUT = int(os.getenv("LLM_REQUEST_TIMEOUT", "45"))
    CONCURRENT_EXECUTION_TIMEOUT = int(os.getenv("CONCURRENT_EXECUTION_TIMEOUT", "70"))
    
    # Orchestration Model Requirements
    MINIMUM_MODELS_REQUIRED = int(os.getenv("MINIMUM_MODELS_REQUIRED", "2"))
    ENABLE_SINGLE_MODEL_FALLBACK = os.getenv("ENABLE_SINGLE_MODEL_FALLBACK", "false").lower() == "true"

    # Retry configuration (aligns with legacy app.config.Config)
    MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    RETRY_INITIAL_DELAY = float(os.getenv("RETRY_INITIAL_DELAY", "1.0"))
    RETRY_MAX_DELAY = float(os.getenv("RETRY_MAX_DELAY", "60.0"))
    RETRY_EXPONENTIAL_BASE = float(os.getenv("RETRY_EXPONENTIAL_BASE", "2.0"))
    RATE_LIMIT_DETECTION_ENABLED = (
        os.getenv("RATE_LIMIT_DETECTION_ENABLED", "true").lower() == "true"
    )
    RATE_LIMIT_RETRY_ENABLED = (
        os.getenv("RATE_LIMIT_RETRY_ENABLED", "true").lower() == "true"
    )

    # Authentication
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "true").lower() == "true"
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ultra.db")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))

    # Redis Cache
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))

    # Feature flags
    ENABLE_MOCK_LLM = os.getenv("ENABLE_MOCK_LLM", "false").lower() == "true"
    ENABLE_RATE_LIMIT = os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true"
    ENABLE_SECURITY_HEADERS = (
        os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
    )
    ENABLE_HTTPS_REDIRECT = (
        os.getenv("ENABLE_HTTPS_REDIRECT", "false").lower() == "true"
    )

    # Monitoring and metrics
    METRICS_ENABLED = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", "8081"))
    SYSTEM_METRICS_INTERVAL = int(os.getenv("SYSTEM_METRICS_INTERVAL", "15"))

    # Security
    API_KEY_ENCRYPTION_KEY = os.getenv("API_KEY_ENCRYPTION_KEY")

    # LLM API Keys (loaded if not in mock mode)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None

    # Public paths for authentication
    PUBLIC_PATHS: List[str] = [
        "/health",
        "/ping",
        "/api/health",
        "/api/debug/ping",
        "/api/debug/config",
        "/api/debug/env",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/refresh",
        "/api/auth/password-reset",
    ]

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories for the application"""
        try:
            os.makedirs(cls.TEMP_UPLOADS_PATH, exist_ok=True)
            os.makedirs(cls.DOCUMENT_STORAGE_PATH, exist_ok=True)
            os.makedirs(cls.TEMP_PATH, exist_ok=True)
            os.makedirs(cls.LOGS_PATH, exist_ok=True)
            logger.info(f"Created required directories")
        except (OSError, PermissionError) as e:
            # If we can't create directories (e.g., in Docker with read-only filesystem)
            # just log a warning and continue - the app will use in-memory storage
            logger.warning(f"Failed to create some directories: {str(e)}")
            logger.warning("Will use in-memory fallbacks where possible")

    @classmethod
    def validate_configuration(cls) -> None:
        """Validate the configuration and load sensitive values"""
        errors = []

        # Generate fallback secrets if not provided (for deployment flexibility)
        if not cls.SECRET_KEY:
            cls.SECRET_KEY = "ultrai-secret-key-fallback-for-deployment"
            logger.warning("Using fallback SECRET_KEY - should set proper value in production")

        if not cls.JWT_SECRET:
            cls.JWT_SECRET = "ultrai-jwt-secret-fallback-for-deployment"
            logger.warning("Using fallback JWT_SECRET - should set proper value in production")

        if cls.ENVIRONMENT == "production":
            if not cls.API_KEY_ENCRYPTION_KEY:
                cls.API_KEY_ENCRYPTION_KEY = "ultrai-encryption-key-fallback-for-deployment"
                logger.warning("Using fallback API_KEY_ENCRYPTION_KEY - should set proper value in production")

            # Allow flexible CORS for deployment
            if "*" in cls.CORS_ORIGINS:
                logger.warning("Using wildcard CORS origins - should specify exact origins in production")

        # Load API keys if not in mock mode
        if not cls.USE_MOCK and not cls.MOCK_MODE:
            cls.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            cls.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
            cls.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
            cls.HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

            # Verify at least one API key is available
            if not any([cls.OPENAI_API_KEY, cls.ANTHROPIC_API_KEY, cls.GOOGLE_API_KEY]):
                errors.append(
                    "At least one LLM API key is required when not in mock mode"
                )

            # Check if default provider has an API key
            if cls.DEFAULT_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
                errors.append(
                    "OpenAI API key is required when using OpenAI as default provider"
                )
            elif cls.DEFAULT_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
                errors.append(
                    "Anthropic API key is required when using Anthropic as default provider"
                )
            elif cls.DEFAULT_PROVIDER == "google" and not cls.GOOGLE_API_KEY:
                errors.append(
                    "Google API key is required when using Google as default provider"
                )

        # Raise exception if there are validation errors
        if errors and not cls.TESTING:
            for error in errors:
                logger.error(f"Configuration error: {error}")

            if cls.ENVIRONMENT == "production":
                raise ConfigValidationError(
                    "Invalid configuration for production environment"
                )
            else:
                logger.warning(
                    "Configuration has issues but will continue in non-production environment"
                )

    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """Get all settings as a dictionary for API responses"""
        # Don't include sensitive values
        settings = {
            k: v
            for k, v in cls.__dict__.items()
            if not k.startswith("_")
            and k
            not in [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "GOOGLE_API_KEY",
                "JWT_SECRET",
                "SECRET_KEY",
                "API_KEY_ENCRYPTION_KEY",
            ]
        }

        # Add API key availability status
        settings.update(
            {
                "openai_api_available": bool(cls.OPENAI_API_KEY),
                "anthropic_api_available": bool(cls.ANTHROPIC_API_KEY),
                "google_api_available": bool(cls.GOOGLE_API_KEY),
            }
        )

        return settings

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

    # Metrics Settings
    METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))
    METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"

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
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

    # Default Model Settings
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Timeout Settings (in seconds)
    ORCHESTRATION_TIMEOUT = int(os.getenv("ORCHESTRATION_TIMEOUT", "90"))
    INITIAL_RESPONSE_TIMEOUT = int(os.getenv("INITIAL_RESPONSE_TIMEOUT", "60"))
    PEER_REVIEW_TIMEOUT = int(os.getenv("PEER_REVIEW_TIMEOUT", "90"))
    ULTRA_SYNTHESIS_TIMEOUT = int(os.getenv("ULTRA_SYNTHESIS_TIMEOUT", "60"))
    LLM_REQUEST_TIMEOUT = int(os.getenv("LLM_REQUEST_TIMEOUT", "45"))
    CONCURRENT_EXECUTION_TIMEOUT = int(os.getenv("CONCURRENT_EXECUTION_TIMEOUT", "70"))

    # Retry Settings
    MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    RETRY_INITIAL_DELAY = float(os.getenv("RETRY_INITIAL_DELAY", "1.0"))
    RETRY_MAX_DELAY = float(os.getenv("RETRY_MAX_DELAY", "60.0"))
    RETRY_EXPONENTIAL_BASE = float(os.getenv("RETRY_EXPONENTIAL_BASE", "2.0"))

    # Rate Limiting Settings  
    RATE_LIMIT_DETECTION_ENABLED = os.getenv("RATE_LIMIT_DETECTION_ENABLED", "true").lower() == "true"
    RATE_LIMIT_RETRY_ENABLED = os.getenv("RATE_LIMIT_RETRY_ENABLED", "true").lower() == "true"

    # Multi-model policy
    # Enforce at least N healthy models to keep UltrAI online.
    MINIMUM_MODELS_REQUIRED = int(os.getenv("MINIMUM_MODELS_REQUIRED", "2"))
    # Explicitly control single-model fallback behavior
    ENABLE_SINGLE_MODEL_FALLBACK = os.getenv("ENABLE_SINGLE_MODEL_FALLBACK", "false").lower() == "true"

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories for the application."""
        os.makedirs("logs", exist_ok=True)

    @classmethod
    def validate_configuration(cls) -> None:
        """Validate the application configuration."""
        # Add validation logic here
        pass

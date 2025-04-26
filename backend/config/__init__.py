"""
Configuration initialization module.
"""

from typing import Dict

from .loader import load_environment_settings
from .settings import Settings


def init_config() -> Dict:
    """Initialize configuration."""
    # Load base settings
    base_settings = Settings()

    # Load environment-specific settings
    env_settings = load_environment_settings()

    # Merge settings
    config = base_settings.dict()
    config.update(env_settings)

    return config


# Initialize configuration
config = init_config()

# Export configuration
__all__ = ["config", "init_config"]

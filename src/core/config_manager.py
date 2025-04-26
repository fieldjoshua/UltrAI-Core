"""
Configuration Manager - Core component responsible for system configuration management.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigSource(Enum):
    """Configuration sources."""

    FILE = "file"
    ENVIRONMENT = "environment"
    MEMORY = "memory"
    DEFAULT = "default"


@dataclass
class ConfigValue:
    """Configuration value with metadata."""

    value: Any
    source: ConfigSource
    last_updated: float
    is_encrypted: bool = False


class ConfigurationManager:
    """Manages system configuration."""

    def __init__(self, config_dir: Optional[str] = None):
        self._config: Dict[str, ConfigValue] = {}
        self._config_dir = config_dir or os.getenv("ULTRA_CONFIG_DIR", "config")
        self._config_file = os.path.join(self._config_dir, "config.json")
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the configuration manager."""
        if self._initialized:
            logger.warning("Configuration Manager already initialized")
            return

        logger.info("Initializing Configuration Manager")

        try:
            # Create config directory if it doesn't exist
            os.makedirs(self._config_dir, exist_ok=True)

            # Load configuration from file
            await self._load_config_from_file()

            # Load configuration from environment
            await self._load_config_from_environment()

            # Set default values
            await self._set_default_values()

            self._initialized = True
            logger.info("Configuration Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Configuration Manager: {str(e)}")
            raise

    async def _load_config_from_file(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self._config_file):
            logger.info(f"Config file not found: {self._config_file}")
            return

        try:
            with open(self._config_file, "r") as f:
                config_data = json.load(f)

            for key, value in config_data.items():
                self._config[key] = ConfigValue(
                    value=value,
                    source=ConfigSource.FILE,
                    last_updated=os.path.getmtime(self._config_file),
                )

            logger.info(f"Loaded configuration from file: {self._config_file}")

        except Exception as e:
            logger.error(f"Error loading config file: {str(e)}")
            raise

    async def _load_config_from_environment(self) -> None:
        """Load configuration from environment variables."""
        for key, value in os.environ.items():
            if key.startswith("ULTRA_"):
                config_key = key[6:].lower()  # Remove 'ULTRA_' prefix
                self._config[config_key] = ConfigValue(
                    value=value,
                    source=ConfigSource.ENVIRONMENT,
                    last_updated=asyncio.get_event_loop().time(),
                )

        logger.info("Loaded configuration from environment variables")

    async def _set_default_values(self) -> None:
        """Set default configuration values."""
        defaults = {
            "log_level": "INFO",
            "max_connections": 100,
            "timeout": 30,
            "retry_attempts": 3,
            "cache_size": 1000,
            "debug_mode": False,
        }

        for key, value in defaults.items():
            if key not in self._config:
                self._config[key] = ConfigValue(
                    value=value,
                    source=ConfigSource.DEFAULT,
                    last_updated=asyncio.get_event_loop().time(),
                )

        logger.info("Set default configuration values")

    async def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        if not self._initialized:
            raise RuntimeError("Configuration Manager not initialized")

        config_value = self._config.get(key)
        if config_value is None:
            return default

        return config_value.value

    async def set(
        self, key: str, value: Any, source: ConfigSource = ConfigSource.MEMORY
    ) -> None:
        """Set configuration value."""
        if not self._initialized:
            raise RuntimeError("Configuration Manager not initialized")

        async with self._lock:
            self._config[key] = ConfigValue(
                value=value, source=source, last_updated=asyncio.get_event_loop().time()
            )

            # If source is file, save to config file
            if source == ConfigSource.FILE:
                await self._save_config_to_file()

    async def _save_config_to_file(self) -> None:
        """Save configuration to file."""
        try:
            config_data = {
                key: value.value
                for key, value in self._config.items()
                if value.source == ConfigSource.FILE
            }

            with open(self._config_file, "w") as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Saved configuration to file: {self._config_file}")

        except Exception as e:
            logger.error(f"Error saving config file: {str(e)}")
            raise

    async def delete(self, key: str) -> None:
        """Delete configuration value."""
        if not self._initialized:
            raise RuntimeError("Configuration Manager not initialized")

        async with self._lock:
            if key in self._config:
                del self._config[key]

                # If value was from file, save to config file
                if self._config[key].source == ConfigSource.FILE:
                    await self._save_config_to_file()

    async def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        if not self._initialized:
            raise RuntimeError("Configuration Manager not initialized")

        return {key: value.value for key, value in self._config.items()}

    async def get_source(self, key: str) -> Optional[ConfigSource]:
        """Get configuration value source."""
        if not self._initialized:
            raise RuntimeError("Configuration Manager not initialized")

        config_value = self._config.get(key)
        if config_value is None:
            return None

        return config_value.source

    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration values."""
        if not self._initialized:
            raise RuntimeError("Configuration Manager not initialized")

        try:
            # Validate required fields
            required_fields = ["log_level", "max_connections", "timeout"]
            for field in required_fields:
                if field not in config:
                    logger.error(f"Missing required field: {field}")
                    return False

            # Validate field types
            if not isinstance(config["log_level"], str):
                logger.error("log_level must be a string")
                return False

            if not isinstance(config["max_connections"], int):
                logger.error("max_connections must be an integer")
                return False

            if not isinstance(config["timeout"], (int, float)):
                logger.error("timeout must be a number")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating config: {str(e)}")
            return False

    async def shutdown(self) -> None:
        """Shutdown the configuration manager."""
        if not self._initialized:
            return

        logger.info("Shutting down Configuration Manager")

        # Save any pending changes
        await self._save_config_to_file()

        self._initialized = False
        logger.info("Configuration Manager shutdown complete")

    async def get_health(self) -> float:
        """Get configuration manager health score."""
        if not self._initialized:
            return 0.0

        try:
            # Check if config file is accessible
            if os.path.exists(self._config_file):
                with open(self._config_file, "r") as f:
                    json.load(f)

            return 1.0

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return 0.0

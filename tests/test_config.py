"""
Unified test configuration system for Ultra.

This module provides centralized configuration for all test modes,
allowing easy switching between offline, mock, integration, live,
and production testing environments.
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class TestMode(Enum):
    """Testing modes for different environments."""
    OFFLINE = "offline"      # No external dependencies, all mocked
    MOCK = "mock"           # Sophisticated mocks, no real APIs
    INTEGRATION = "int"     # Local services (Redis, DB) but mocked APIs
    LIVE = "live"           # Real API calls to LLM providers
    PRODUCTION = "prod"     # Tests against production endpoints


@dataclass
class TestConfig:
    """Configuration for a specific test mode."""
    mode: TestMode
    use_mocks: bool
    mock_llms: bool
    use_real_redis: bool
    use_real_db: bool
    api_timeout: float
    base_url: str
    require_api_keys: bool
    skip_markers: list[str]
    env_vars: Dict[str, str]


# Test mode configurations
TEST_CONFIGS = {
    TestMode.OFFLINE: TestConfig(
        mode=TestMode.OFFLINE,
        use_mocks=True,
        mock_llms=True,
        use_real_redis=False,
        use_real_db=False,
        api_timeout=5.0,
        base_url="http://testserver",
        require_api_keys=False,
        skip_markers=["live", "live_online", "production", "integration"],
        env_vars={
            "TESTING": "true",
            "USE_MOCK": "true",
            "MOCK_MODE": "true",
            "ENABLE_AUTH": "false",
            "REDIS_URL": "",
            "DATABASE_URL": "",
            "MINIMUM_MODELS_REQUIRED": "1",
            "ENABLE_SINGLE_MODEL_FALLBACK": "true",
            "REQUIRED_PROVIDERS": "openai",
        }
    ),
    TestMode.MOCK: TestConfig(
        mode=TestMode.MOCK,
        use_mocks=True,
        mock_llms=True,
        use_real_redis=False,
        use_real_db=False,
        api_timeout=10.0,
        base_url="http://testserver",
        require_api_keys=False,
        skip_markers=["live", "live_online", "production"],
        env_vars={
            "TESTING": "true",
            "USE_MOCK": "true",
            "MOCK_MODE": "true",
            "ENABLE_AUTH": "true",
            "MOCK_RESPONSES": "sophisticated",
            "MINIMUM_MODELS_REQUIRED": "1",
            "ENABLE_SINGLE_MODEL_FALLBACK": "true",
            "REQUIRED_PROVIDERS": "openai",
        }
    ),
    TestMode.INTEGRATION: TestConfig(
        mode=TestMode.INTEGRATION,
        use_mocks=False,
        mock_llms=True,
        use_real_redis=True,
        use_real_db=True,
        api_timeout=30.0,
        base_url="http://localhost:8000",
        require_api_keys=False,
        skip_markers=["live", "live_online", "production"],
        env_vars={
            "TESTING": "true",
            "USE_MOCK": "true",
            "ENABLE_AUTH": "true",
            "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "DATABASE_URL": os.getenv("TEST_DATABASE_URL", "postgresql://localhost/ultra_test"),
            "MINIMUM_MODELS_REQUIRED": "1",
            "ENABLE_SINGLE_MODEL_FALLBACK": "true",
            "REQUIRED_PROVIDERS": "openai",
        }
    ),
    TestMode.LIVE: TestConfig(
        mode=TestMode.LIVE,
        use_mocks=False,
        mock_llms=False,
        use_real_redis=True,
        use_real_db=True,
        api_timeout=60.0,
        base_url="http://localhost:8000",
        require_api_keys=True,
        skip_markers=["production"],
        env_vars={
            "TESTING": "true",
            "USE_MOCK": "false",
            "ENABLE_AUTH": "true",
            "REQUIRE_API_KEYS": "true",
        }
    ),
    TestMode.PRODUCTION: TestConfig(
        mode=TestMode.PRODUCTION,
        use_mocks=False,
        mock_llms=False,
        use_real_redis=False,
        use_real_db=False,
        api_timeout=60.0,
        base_url="https://ultrai-core.onrender.com",
        require_api_keys=True,
        skip_markers=[],
        env_vars={
            "TESTING": "false",
            "USE_MOCK": "false",
            "ENABLE_AUTH": "true",
            "TEST_PRODUCTION_API": "true",
        }
    ),
}


class TestConfiguration:
    """Singleton test configuration manager."""
    
    _instance = None
    _config: Optional[TestConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self):
        """Load configuration based on TEST_MODE environment variable."""
        mode_str = os.getenv("TEST_MODE", "offline").lower()
        
        # Map string to enum
        mode_map = {
            "offline": TestMode.OFFLINE,
            "mock": TestMode.MOCK,
            "int": TestMode.INTEGRATION,
            "integration": TestMode.INTEGRATION,
            "live": TestMode.LIVE,
            "prod": TestMode.PRODUCTION,
            "production": TestMode.PRODUCTION,
        }
        
        mode = mode_map.get(mode_str, TestMode.OFFLINE)
        self._config = TEST_CONFIGS[mode]
        
        # Apply environment variables
        for key, value in self._config.env_vars.items():
            if key not in os.environ:  # Don't override existing values
                os.environ[key] = value
    
    @property
    def config(self) -> TestConfig:
        """Get current test configuration."""
        if self._config is None:
            self.load_config()
        return self._config
    
    @property
    def mode(self) -> TestMode:
        """Get current test mode."""
        return self.config.mode
    
    def should_skip(self, markers: list[str]) -> bool:
        """Check if test should be skipped based on markers."""
        return any(marker in self.config.skip_markers for marker in markers)
    
    def get_client_kwargs(self) -> Dict[str, Any]:
        """Get kwargs for test client creation."""
        return {
            "base_url": self.config.base_url,
            "timeout": self.config.api_timeout,
        }
    
    def require_api_keys(self) -> bool:
        """Check if API keys are required."""
        if not self.config.require_api_keys:
            return True
        
        required_keys = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY", 
            "GOOGLE_API_KEY",
            "HUGGINGFACE_API_TOKEN"
        ]
        
        return all(os.getenv(key) for key in required_keys)


# Global instance
test_config = TestConfiguration()


# Decorator for mode-specific tests
def requires_mode(*modes: TestMode):
    """Decorator to mark tests for specific modes."""
    import pytest
    
    def decorator(func):
        current_mode = test_config.mode
        if current_mode not in modes:
            return pytest.mark.skip(
                f"Test requires mode {modes}, current mode is {current_mode}"
            )(func)
        return func
    
    return decorator


# Decorator for conditional skipping
def skip_in_modes(*modes: TestMode):
    """Decorator to skip tests in specific modes."""
    import pytest
    
    def decorator(func):
        current_mode = test_config.mode
        if current_mode in modes:
            return pytest.mark.skip(
                f"Test skipped in mode {current_mode}"
            )(func)
        return func
    
    return decorator


# Helper decorators for backward compatibility
def skip_if_offline():
    """Skip test if in offline mode."""
    import pytest
    def decorator(func):
        if test_config.mode == TestMode.OFFLINE:
            return pytest.mark.skip("Test skipped in OFFLINE mode")(func)
        return func
    return decorator


def skip_if_not_mode(mode: TestMode):
    """Skip test if not in specified mode."""
    import pytest
    def decorator(func):
        if test_config.mode != mode:
            return pytest.mark.skip(f"Test requires {mode} mode")(func)
        return func
    return decorator
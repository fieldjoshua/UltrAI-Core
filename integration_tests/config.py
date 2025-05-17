"""Integration Test Configuration"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ServiceConfig:
    """Service configuration"""

    name: str
    url: str
    health_endpoint: str = "/health"
    timeout: int = 30


@dataclass
class TestEnvironment:
    """Test environment configuration"""

    name: str
    api_base_url: str
    database_url: str
    redis_url: str
    services: Dict[str, ServiceConfig]

    @property
    def is_production(self) -> bool:
        return self.name == "production"

    @property
    def is_staging(self) -> bool:
        return self.name == "staging"

    @property
    def is_local(self) -> bool:
        return self.name == "local"


# Environment configurations
ENVIRONMENTS = {
    "local": TestEnvironment(
        name="local",
        api_base_url="http://localhost:8087/api",
        database_url="postgresql://ultra_test:test_password@localhost:5433/ultra_test",
        redis_url="redis://localhost:6380",
        services={
            "api": ServiceConfig("api", "http://localhost:8087", "/api/health"),
            "mock_llm": ServiceConfig("mock_llm", "http://localhost:8086", "/health"),
            "postgres": ServiceConfig("postgres", "http://localhost:5433", ""),
            "redis": ServiceConfig("redis", "http://localhost:6380", ""),
        },
    ),
    "docker": TestEnvironment(
        name="docker",
        api_base_url="http://test-app:8085/api",
        database_url="postgresql://ultra_test:test_password@test-db:5432/ultra_test",
        redis_url="redis://test-redis:6379",
        services={
            "api": ServiceConfig("api", "http://test-app:8085", "/api/health"),
            "mock_llm": ServiceConfig("mock_llm", "http://mock-llm:8086", "/health"),
            "postgres": ServiceConfig("postgres", "http://test-db:5432", ""),
            "redis": ServiceConfig("redis", "http://test-redis:6379", ""),
        },
    ),
    "staging": TestEnvironment(
        name="staging",
        api_base_url="https://staging.ultra.ai/api",
        database_url=os.getenv("STAGING_DATABASE_URL", ""),
        redis_url=os.getenv("STAGING_REDIS_URL", ""),
        services={
            "api": ServiceConfig("api", "https://staging.ultra.ai", "/api/health"),
        },
    ),
    "production": TestEnvironment(
        name="production",
        api_base_url="https://api.ultra.ai",
        database_url=os.getenv("PROD_DATABASE_URL", ""),
        redis_url=os.getenv("PROD_REDIS_URL", ""),
        services={
            "api": ServiceConfig("api", "https://api.ultra.ai", "/api/health"),
        },
    ),
}

# Get current environment
CURRENT_ENV_NAME = os.getenv("TEST_ENV", "local")
CURRENT_ENV = ENVIRONMENTS.get(CURRENT_ENV_NAME, ENVIRONMENTS["local"])


@dataclass
class TestConfig:
    """Global test configuration"""

    environment: TestEnvironment

    # Timeouts
    default_timeout: int = 30
    health_check_timeout: int = 60
    load_test_timeout: int = 300

    # Test settings
    enable_cleanup: bool = True
    verbose_logging: bool = False
    capture_screenshots: bool = True

    # Performance thresholds
    max_response_time: float = 2.0  # seconds
    max_error_rate: float = 0.01  # 1%

    # Load test settings
    max_concurrent_users: int = 100
    requests_per_second: int = 50

    # File paths
    test_data_dir: str = (
        "/Users/joshuafield/Documents/Ultra/integration_tests/fixtures/test_data"
    )
    screenshots_dir: str = (
        "/Users/joshuafield/Documents/Ultra/integration_tests/screenshots"
    )
    reports_dir: str = "/Users/joshuafield/Documents/Ultra/integration_tests/reports"

    # API Keys (for testing real providers)
    test_api_keys: Dict[str, str] = None

    def __post_init__(self):
        """Load additional configuration"""
        # Load test API keys if available
        if os.path.exists(".env.test.keys"):
            import dotenv

            env_vars = dotenv.dotenv_values(".env.test.keys")
            self.test_api_keys = {
                "openai": env_vars.get("OPENAI_API_KEY"),
                "anthropic": env_vars.get("ANTHROPIC_API_KEY"),
                "google": env_vars.get("GOOGLE_API_KEY"),
            }

        # Create directories if they don't exist
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)


# Create global config instance
CONFIG = TestConfig(environment=CURRENT_ENV)

# Test categories for selective execution
TEST_CATEGORIES = {
    "smoke": ["test_health_endpoints", "test_basic_auth", "test_simple_analysis"],
    "auth": [
        "test_registration",
        "test_login",
        "test_token_refresh",
        "test_permissions",
    ],
    "api": [
        "test_document_upload",
        "test_analysis_request",
        "test_result_retrieval",
        "test_error_handling",
    ],
    "integration": [
        "test_full_analysis_flow",
        "test_concurrent_requests",
        "test_llm_fallback",
        "test_caching",
    ],
    "performance": [
        "test_load_ramp_up",
        "test_sustained_load",
        "test_spike_test",
        "test_large_documents",
    ],
    "security": [
        "test_authentication",
        "test_authorization",
        "test_input_validation",
        "test_rate_limiting",
    ],
    "resilience": [
        "test_service_recovery",
        "test_circuit_breaker",
        "test_retry_logic",
        "test_graceful_degradation",
    ],
}

# Test data profiles
TEST_PROFILES = {
    "small": {"document_size": 1024, "concurrent_users": 5, "duration": 60},  # 1KB
    "medium": {
        "document_size": 1024 * 100,  # 100KB
        "concurrent_users": 20,
        "duration": 300,
    },
    "large": {
        "document_size": 1024 * 1024 * 10,  # 10MB
        "concurrent_users": 50,
        "duration": 600,
    },
    "stress": {
        "document_size": 1024 * 1024 * 50,  # 50MB
        "concurrent_users": 100,
        "duration": 1800,
    },
}


def get_test_profile(profile_name: str = "medium") -> Dict:
    """Get test profile configuration"""
    return TEST_PROFILES.get(profile_name, TEST_PROFILES["medium"])


def get_test_categories(category: str = "all") -> List[str]:
    """Get tests for a specific category"""
    if category == "all":
        return [test for tests in TEST_CATEGORIES.values() for test in tests]
    return TEST_CATEGORIES.get(category, [])


# Export configuration
__all__ = [
    "CONFIG",
    "CURRENT_ENV",
    "TEST_CATEGORIES",
    "TEST_PROFILES",
    "get_test_profile",
    "get_test_categories",
]

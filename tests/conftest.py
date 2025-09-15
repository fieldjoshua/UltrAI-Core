import sys
import os
import asyncio
import importlib.metadata as _metadata
import httpx  # noqa: E402
from typing import Any, Dict  # noqa: E402
from unittest.mock import AsyncMock, MagicMock, patch  # noqa: E402

# Set environment before any imports
test_mode = os.getenv("TEST_MODE", "offline").lower()
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

# Import test configuration after environment is set
from .test_config import test_config, TestMode  # noqa: E402
from .mock_config import get_mock_llm_adapters, get_mock_services  # noqa: E402

# Fake version for email-validator to satisfy Pydantic networks import
_orig_version = _metadata.version


def version(name: str) -> str:
    if name == "email-validator":
        return "2.0.0"
    return _orig_version(name)


_metadata.version = version

# Add project root to PYTHONPATH so tests can import the `app` package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ---------------------------------------------------------------------------
# Fix for async event loop conflicts
# ---------------------------------------------------------------------------

# Check if we're in a Jupyter-like environment
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

# Force pytest-asyncio to use function-scoped event loops
import pytest_asyncio
pytest_asyncio.fixture(scope="function")

# Configure asyncio for tests
import pytest
pytest_plugins = ('pytest_asyncio',)

# Register custom markers
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "requires_redis: mark test as requiring Redis")
    config.addinivalue_line("markers", "requires_api_keys: mark test as requiring API keys")
    config.addinivalue_line("markers", "slow: mark test as slow (>1 second)")
    config.addinivalue_line("markers", "live_online: mark test as requiring live online services")

# No mocking - tests will use real network calls

# (OpenAIAdapter stub removed – real adapter will be used with individual tests patching requests)

# ---------------------------------------------------------------------------
# Playwright configuration to use system-installed Chrome instead of bundled browser
# ---------------------------------------------------------------------------

# Fixture recognised by pytest-playwright across versions

import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Launch Playwright using the local Chrome executable in headless mode."""

    chrome_path = os.getenv(
        "CHROME_EXECUTABLE",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    )
    return {"executable_path": chrome_path, "headless": True}


# ---------------------------------------------------------------------------
# Provide proper async event loop fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    # Ensure all tasks are complete
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    # Run until all tasks are cancelled
    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    loop.close()


# ---------------------------------------------------------------------------
# Configure mocking based on test mode
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def configure_test_environment(monkeypatch):
    """Automatically configure test environment based on TEST_MODE"""
    # Apply test mode configuration
    config = test_config.config
    
    # Set all environment variables for this mode
    for key, value in config.env_vars.items():
        monkeypatch.setenv(key, value)
    
    # Log test mode for debugging
    import logging
    logging.info(f"Running tests in {config.mode.value} mode")


@pytest.fixture
def mock_llm_adapters():
    """Provide mock LLM adapters when not in LIVE mode"""
    config = test_config.config
    if config.mock_llms:
        # Get pre-configured mocks from mock_config
        mocks = get_mock_llm_adapters()
        
        with patch("app.services.orchestration_service.OpenAIAdapter", mocks["openai"]), \
             patch("app.services.orchestration_service.AnthropicAdapter", mocks["anthropic"]), \
             patch("app.services.orchestration_service.GeminiAdapter", mocks["gemini"]), \
             patch("app.services.orchestration_service.HuggingFaceAdapter", mocks["huggingface"]):
            
            yield mocks
    else:
        yield None


@pytest.fixture
def mock_redis():
    """Provide mock Redis when not in INTEGRATION/LIVE mode"""
    config = test_config.config
    if not config.use_real_redis:
        with patch("redis.asyncio.Redis") as mock_redis_cls:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=None)
            mock_instance.set = AsyncMock(return_value=True)
            mock_instance.delete = AsyncMock(return_value=1)
            mock_instance.exists = AsyncMock(return_value=False)
            mock_instance.expire = AsyncMock(return_value=True)
            mock_redis_cls.from_url.return_value = mock_instance
            yield mock_instance
    else:
        yield None


@pytest.fixture
def mock_database():
    """Provide mock database when in OFFLINE mode"""
    config = test_config.config
    if not config.use_real_db:
        with patch("sqlalchemy.create_engine") as mock_engine, \
             patch("sqlalchemy.orm.sessionmaker") as mock_session:
            # Configure mock database
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            yield mock_session_instance
    else:
        yield None


@pytest.fixture
def test_client():
    """Provide test client configured for current test mode"""
    from httpx import AsyncClient
    
    kwargs = test_config.get_client_kwargs()
    return AsyncClient(**kwargs)


# ---------------------------------------------------------------------------
# Pytest markers configuration based on test mode
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """Configure pytest based on test mode"""
    # Get current marks from command line
    markexpr = config.getoption("-m", "")
    
    # Modify marks based on test mode
    if test_config.mode == TestMode.OFFLINE:
        # In offline mode, skip live, integration, and production tests
        if not markexpr:
            config.option.markexpr = "not live and not live_online and not integration and not production"
    elif test_config.mode == TestMode.MOCK:
        # In mock mode, skip live and production tests
        if not markexpr:
            config.option.markexpr = "not live and not live_online and not production"
    elif test_config.mode == TestMode.INTEGRATION:
        # In integration mode, skip live and production tests
        if not markexpr:
            config.option.markexpr = "not live and not live_online and not production"
    elif test_config.mode == TestMode.LIVE:
        # In live mode, skip only production tests
        if not markexpr:
            config.option.markexpr = "not production"
    # TestMode.PRODUCTION runs all tests


# No stubbing - all tests will use real implementations or explicit mocks
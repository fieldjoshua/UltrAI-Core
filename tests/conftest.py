"""
Pytest configuration and fixtures for all tests
"""
import pytest
import asyncio
import httpx
from typing import AsyncGenerator

# Production API URL
PRODUCTION_URL = "https://ultrai-core.onrender.com"

@pytest.fixture
def production_url():
    """Production API URL fixture"""
    return PRODUCTION_URL

@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client fixture"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client

@pytest.fixture
def sync_client():
    """Sync HTTP client fixture"""
    with httpx.Client(timeout=30.0) as client:
        yield client

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "production: marks tests as production tests")
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "quick: marks tests as quick")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
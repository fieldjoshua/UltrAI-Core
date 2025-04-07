import os
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app and set up mock mode
from main import app, Config

# Setup test fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def client():
    """Create a TestClient for testing sync endpoints"""
    # Enable mock mode for testing
    Config.use_mock = True
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
async def async_client():
    """Create an AsyncClient for testing async endpoints"""
    # Enable mock mode for testing
    Config.use_mock = True
    
    # Create async test client
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
def test_document_file(tmp_path):
    """Create a test document file for document upload tests"""
    file_path = tmp_path / "test_document.txt"
    with open(file_path, "w") as f:
        f.write("This is a test document content for document processing tests.")
    return file_path

@pytest.fixture
def mock_environment():
    """Set up environment variables for testing"""
    old_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["TEST_MODE"] = "True"
    os.environ["SENTRY_ENVIRONMENT"] = "test"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(old_env) 
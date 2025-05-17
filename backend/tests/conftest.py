import asyncio
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app and config
import os
from pathlib import Path

from dotenv import load_dotenv

# Load test environment variables
test_env_file = Path(__file__).parent.parent.parent / ".env.testing"
if test_env_file.exists():
    load_dotenv(dotenv_path=str(test_env_file))
else:
    # Set minimal test environment if file doesn't exist
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["TESTING"] = "true"
    os.environ["USE_MOCK"] = "true"
    os.environ["MOCK_MODE"] = "true"

# Now import the app and config
from app import app
from backend.config import Config

# For backward compatibility with existing tests
try:
    from main import app as main_app
except ImportError:
    # Use backend app if main app is not found
    main_app = app

# Test data constants
MOCK_PROVIDERS = {
    "openai": {"name": "OpenAI", "models": ["gpt-3.5-turbo", "gpt-4"], "enabled": True},
    "anthropic": {
        "name": "Anthropic",
        "models": ["claude-2.1", "claude-3-opus"],
        "enabled": True,
    },
    "google": {
        "name": "Google",
        "models": ["gemini-pro", "gemini-1.5-pro"],
        "enabled": False,
    },
    "mistral": {
        "name": "Mistral AI",
        "models": ["mistral-small", "mistral-medium", "mistral-large"],
        "enabled": True,
    },
}

MOCK_ANALYSIS_PATTERNS = [
    {
        "id": "code_review",
        "name": "Code Review",
        "description": "Analyzes code for best practices, bugs, and readability",
        "prompt_template": "Review this code: {content}. Identify potential bugs, style issues, and suggest improvements.",
    },
    {
        "id": "security_audit",
        "name": "Security Audit",
        "description": "Checks code for security vulnerabilities",
        "prompt_template": "Perform a security audit on this code: {content}. Identify potential vulnerabilities, insecure practices, and suggest fixes.",
    },
    {
        "id": "documentation",
        "name": "Documentation Generator",
        "description": "Generates documentation for code",
        "prompt_template": "Generate documentation for this code: {content}. Include function descriptions, parameter details, and usage examples.",
    },
]

MOCK_LLM_RESPONSE = {
    "text": "This is a mock response from the LLM service.",
    "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
}


# Setup test fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client():
    """Create a TestClient for testing sync endpoints (using main app for backward compatibility)"""
    # Configure testing environment
    Config.TESTING = True
    Config.USE_MOCK = os.environ.get("USE_MOCK", "true").lower() == "true"
    Config.MOCK_MODE = os.environ.get("MOCK_MODE", "true").lower() == "true"

    # Set up test token for all requests
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjk5OTk5OTk5OTl9.c14U6E_qhXlULTAW9zBCHpjdIXGXpYi7fdLdyHJl4wo"

    # Create test client
    with TestClient(main_app) as test_client:
        # Add authentication header to all requests
        test_client.headers.update(
            {
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
                "X-Test-Client": "true",
            }
        )

        yield test_client


@pytest.fixture(scope="module")
def test_client():
    """Create a TestClient for testing sync endpoints with the backend app"""
    # Configure testing environment
    Config.TESTING = True
    Config.USE_MOCK = os.environ.get("USE_MOCK", "true").lower() == "true"
    Config.MOCK_MODE = os.environ.get("MOCK_MODE", "true").lower() == "true"

    # Set up test token for all requests
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjk5OTk5OTk5OTl9.c14U6E_qhXlULTAW9zBCHpjdIXGXpYi7fdLdyHJl4wo"

    with TestClient(app) as client:
        # Add authentication header to all requests
        client.headers.update(
            {
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
                "X-Test-Client": "true",
            }
        )

        yield client


@pytest.fixture(scope="module")
async def async_client():
    """Create an AsyncClient for testing async endpoints"""
    # Configure testing environment
    Config.TESTING = True
    Config.USE_MOCK = os.environ.get("USE_MOCK", "true").lower() == "true"
    Config.MOCK_MODE = os.environ.get("MOCK_MODE", "true").lower() == "true"

    # Set up test token for all requests
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjk5OTk5OTk5OTl9.c14U6E_qhXlULTAW9zBCHpjdIXGXpYi7fdLdyHJl4wo"

    # Create async test client
    async with AsyncClient(app=main_app, base_url="http://test") as ac:
        # Add authentication header to all requests
        ac.headers.update(
            {
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
                "X-Test-Client": "true",
            }
        )

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
    os.environ["MOCK_MODE"] = "true"
    os.environ["SENTRY_ENVIRONMENT"] = "test"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "true"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def mock_settings():
    """Mock settings with test data"""
    settings = MagicMock()
    settings.MODEL_PROVIDERS = MOCK_PROVIDERS
    settings.ANALYSIS_PATTERNS = MOCK_ANALYSIS_PATTERNS
    settings.use_mock = True
    settings.DEBUG = True
    return settings


@pytest.fixture
def mock_get_settings(mock_settings):
    """Override settings for testing"""
    original_mock = Config.use_mock
    Config.use_mock = True
    yield
    Config.use_mock = original_mock


@pytest.fixture
def mock_env_vars():
    """Set test environment variables and restore them after the test"""
    original_env = os.environ.copy()

    # Set test environment variables
    test_vars = {
        "ENVIRONMENT": "testing",
        "TESTING": "true",
        "DEBUG": "true",
        "USE_MOCK": os.environ.get("USE_MOCK", "true"),
        "MOCK_MODE": os.environ.get("MOCK_MODE", "true"),
        "ENABLE_AUTH": "true",
        "JWT_SECRET": "test-jwt-secret",
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "GOOGLE_API_KEY": "test-google-key",
        "DEFAULT_PROVIDER": "openai",
        "DEFAULT_MODEL": "gpt-4o",
        "REDIS_URL": "redis://localhost:6379/1",
        "DATABASE_URL": "sqlite:///:memory:",
        "CORS_ORIGINS": "*",
        "SENTRY_DSN": "",  # Empty to disable Sentry during tests
    }

    os.environ.update(test_vars)

    # Update config with test settings
    Config.TESTING = True
    Config.USE_MOCK = test_vars["USE_MOCK"].lower() == "true"
    Config.MOCK_MODE = test_vars["MOCK_MODE"].lower() == "true"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_llm_service():
    """Mock the LLM service to return a predefined response"""
    with patch(
        "backend.services.llm_service.query_llm", return_value=MOCK_LLM_RESPONSE
    ) as mock:
        yield mock


@pytest.fixture
def sample_content():
    """Sample content for testing analysis endpoints"""
    return """
def add_numbers(a, b):
    \"\"\"Add two numbers and return the result.\"\"\"
    return a + b

def divide_numbers(a, b):
    \"\"\"Divide two numbers.\"\"\"
    return a / b  # Potential division by zero error

# Example credentials for testing
API_KEY = "test_fake_key_for_demonstration"

def main():
    print(add_numbers(5, 10))
    print(divide_numbers(10, 2))

if __name__ == "__main__":
    main()
"""

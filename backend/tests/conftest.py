import asyncio
import os
import sys

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from typing import Dict, Any
from backend.core.llm import LLMProvider, PromptManager, ResponseProcessor
from backend.core.orchestration import Pattern, OrchestrationEngine
from backend.core.api import APIRouter, APIResponse
from backend.core.frontend import FrontendConfig, FrontendComponent
from backend.core.integration import Service, ServiceRegistry
from backend.core.data import StoragePattern, PersistenceStrategy, DataFlow

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app and set up mock mode
from main import Config, app


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


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""

    class MockLLMProvider(LLMProvider):
        async def generate(self, prompt: str, **kwargs) -> str:
            return f"Mock response for: {prompt}"

        async def stream(self, prompt: str, **kwargs) -> str:
            return f"Mock stream for: {prompt}"

    return MockLLMProvider("test_key", "test_model")


@pytest.fixture
def prompt_manager():
    """Prompt manager for testing."""
    manager = PromptManager()
    manager.add_template("test", "Test template: {input}")
    return manager


@pytest.fixture
def response_processor():
    """Response processor for testing."""
    processor = ResponseProcessor()
    processor.add_validator(lambda x: bool(x.strip()))
    return processor


@pytest.fixture
def pattern():
    """Test pattern for orchestration."""
    pattern = Pattern("test_pattern", "Test pattern description")
    pattern.add_step({"template": "test", "type": "generation"})
    return pattern


@pytest.fixture
def orchestration_engine(mock_llm_provider, prompt_manager, response_processor):
    """Orchestration engine with all dependencies."""
    engine = OrchestrationEngine()
    engine.set_llm_provider(mock_llm_provider)
    engine.set_prompt_manager(prompt_manager)
    engine.set_response_processor(response_processor)
    return engine


@pytest.fixture
def api_router():
    """API router for testing."""
    return APIRouter()


@pytest.fixture
def frontend_config():
    """Frontend configuration for testing."""
    return FrontendConfig(
        title="Test App",
        description="Test application",
        version="1.0.0",
        theme={"primary": "#000000"},
    )


@pytest.fixture
def frontend_component(frontend_config):
    """Frontend component with configuration."""
    return FrontendComponent(frontend_config)


@pytest.fixture
def mock_service():
    """Mock service for testing."""

    class MockService(Service):
        async def initialize(self) -> None:
            pass

        async def shutdown(self) -> None:
            pass

    return MockService()


@pytest.fixture
def service_registry(mock_service):
    """Service registry with mock service."""
    registry = ServiceRegistry()
    registry.register_service("test_service", mock_service)
    return registry


@pytest.fixture
def mock_storage_pattern():
    """Mock storage pattern for testing."""

    class MockStoragePattern(StoragePattern):
        async def store(self, data: Any) -> None:
            pass

        async def retrieve(self, identifier: str) -> Any:
            return {"id": identifier, "data": "test"}

        async def update(self, identifier: str, data: Any) -> None:
            pass

        async def delete(self, identifier: str) -> None:
            pass

    return MockStoragePattern()


@pytest.fixture
def mock_persistence_strategy():
    """Mock persistence strategy for testing."""

    class MockPersistenceStrategy(PersistenceStrategy):
        async def save(self, data: Any) -> str:
            return "test_id"

        async def load(self, identifier: str) -> Any:
            return {"id": identifier, "data": "test"}

        async def remove(self, identifier: str) -> None:
            pass

    return MockPersistenceStrategy()


@pytest.fixture
def data_flow(mock_storage_pattern, mock_persistence_strategy):
    """Data flow with mock patterns and strategies."""
    flow = DataFlow()
    flow.register_pattern("test_pattern", mock_storage_pattern)
    flow.register_strategy("test_strategy", mock_persistence_strategy)
    return flow

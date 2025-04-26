import pytest
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from src.orchestrator import TriLLMOrchestrator
from src.models import ModelResponse, QualityMetrics

# Load test environment variables
load_dotenv(".env.test")


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    os.environ["TESTING"] = "true"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    yield
    # Clean up after tests
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
    if "JWT_SECRET_KEY" in os.environ:
        del os.environ["JWT_SECRET_KEY"]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "cache_enabled": True,
        "max_retries": 3,
        "response_timeout": 5.0,
        "quality_threshold": 0.7,
    }


@pytest.fixture(scope="session")
def mock_llm_responses():
    """Provide sample LLM responses for testing."""
    return {
        "llama": "Llama response with technical insights",
        "chatgpt": "ChatGPT response with strategic analysis",
        "gemini": "Gemini response with unique perspectives",
    }


@pytest.fixture(scope="session")
def sample_quality_metrics():
    """Provide sample quality metrics for testing."""
    return QualityMetrics(
        coherence_score=0.8, technical_depth=0.9, strategic_value=0.85, uniqueness=0.75
    )


@pytest.fixture(scope="session")
def sample_model_response(sample_quality_metrics):
    """Provide a sample model response for testing."""
    return ModelResponse(
        model_name="TestModel",
        content="Sample response content",
        stage="test",
        timestamp=datetime.now().timestamp(),
        tokens_used=100,
        quality=sample_quality_metrics,
    )

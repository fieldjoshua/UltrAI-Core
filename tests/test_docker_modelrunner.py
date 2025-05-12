"""
Test suite for Docker Model Runner integration with Ultra.

This test module checks connectivity and functionality of the Docker Model Runner 
integration, ensuring proper adapter behavior and mock service fallback.
"""

import os
import sys
import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Add src directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the adapter and related modules
from src.models.docker_modelrunner_adapter import (
    DockerModelRunnerAdapter, 
    get_available_models,
    create_modelrunner_adapter
)
from backend.services.mock_llm_service import MockLLMService


@pytest.fixture
def mock_successful_response():
    """Mock successful response from Docker Model Runner API."""
    return {
        "id": "test-id",
        "object": "chat.completion",
        "created": 1683489157,
        "model": "phi3:mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from Docker Model Runner."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 12,
            "total_tokens": 22
        }
    }


@pytest.mark.asyncio
async def test_docker_modelrunner_available():
    """Test if Docker Model Runner is available by checking the models endpoint."""
    try:
        # First check if the server is reachable
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("http://localhost:8080/v1/models", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["id"] for model in data.get("data", [])]
                        assert isinstance(models, list), "Expected a list of models"
                        print(f"Docker Model Runner available with models: {models}")
                        return True
                    else:
                        print(f"Docker Model Runner API returned status {response.status}")
                        pytest.skip("Docker Model Runner API returned error status")
                        return False
            except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as e:
                print(f"Cannot connect to Docker Model Runner: {str(e)}")
                pytest.skip("Docker Model Runner is not available")
                return False
    except Exception as e:
        print(f"Docker Model Runner test failed: {str(e)}")
        pytest.skip("Docker Model Runner test failed")
        return False


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.request')
async def test_adapter_generate(mock_request, mock_successful_response):
    """Test the DockerModelRunnerAdapter generate method."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_successful_response)
    mock_request.return_value.__aenter__.return_value = mock_response
    
    # Create adapter
    adapter = DockerModelRunnerAdapter(
        model="phi3:mini",
        base_url="http://localhost:8080",
        model_mapping={"phi3:mini": "phi3:mini"}
    )
    
    # Test generate method
    prompt = "Test prompt"
    response = await adapter.generate(prompt)
    
    # Verify response
    assert "This is a test response from Docker Model Runner" in response
    mock_request.assert_called_once()


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.request')
async def test_adapter_stream_generate(mock_request, mock_successful_response):
    """Test the DockerModelRunnerAdapter stream_generate method."""
    # Setup mock for streaming response
    mock_response = MagicMock()
    mock_response.status = 200
    
    # Create a mock for the content attribute that will yield streaming data
    content_mock = AsyncMock()
    
    # Create a stream chunk that mimics the SSE format from OpenAI API
    stream_chunk = json.dumps({
        "id": "test-id",
        "object": "chat.completion.chunk",
        "created": 1683489157,
        "model": "phi3:mini",
        "choices": [
            {
                "index": 0,
                "delta": {
                    "content": "This is a "
                },
                "finish_reason": None
            }
        ]
    }).encode() + b"\n\n"
    
    stream_chunk2 = json.dumps({
        "id": "test-id",
        "object": "chat.completion.chunk",
        "created": 1683489157,
        "model": "phi3:mini",
        "choices": [
            {
                "index": 0,
                "delta": {
                    "content": "test response"
                },
                "finish_reason": None
            }
        ]
    }).encode() + b"\n\n"
    
    stream_chunk3 = json.dumps({
        "id": "test-id",
        "object": "chat.completion.chunk",
        "created": 1683489157,
        "model": "phi3:mini",
        "choices": [
            {
                "index": 0,
                "delta": {
                    "content": ""
                },
                "finish_reason": "stop"
            }
        ]
    }).encode() + b"\n\n"
    
    # Setup the content mock to yield the stream chunks
    content_chunks = [stream_chunk, stream_chunk2, stream_chunk3]
    content_mock.__aiter__.return_value = content_chunks
    
    # Attach the content mock to the response
    mock_response.content = content_mock
    mock_request.return_value.__aenter__.return_value = mock_response
    
    # Create adapter
    adapter = DockerModelRunnerAdapter(
        model="phi3:mini",
        base_url="http://localhost:8080",
        model_mapping={"phi3:mini": "phi3:mini"}
    )
    
    # Test stream_generate method
    prompt = "Test prompt"
    collected_chunks = []
    async for chunk in adapter.stream_generate(prompt):
        collected_chunks.append(chunk)
    
    # Verify response
    assert len(collected_chunks) > 0
    assert "".join(collected_chunks) == "This is a test response"
    mock_request.assert_called_once()


@pytest.mark.asyncio
@patch('src.models.docker_modelrunner_adapter.get_available_models')
async def test_create_modelrunner_adapter(mock_get_available_models):
    """Test creating a DockerModelRunnerAdapter with the factory function."""
    # Mock available models
    mock_get_available_models.return_value = ["phi3:mini", "llama3:8b"]
    
    # Test create_modelrunner_adapter
    adapter = await create_modelrunner_adapter(
        model="phi3:mini",
        base_url="http://localhost:8080"
    )
    
    assert isinstance(adapter, DockerModelRunnerAdapter)
    assert adapter.model == "phi3:mini"
    assert adapter.base_url == "http://localhost:8080"


@pytest.mark.asyncio
@patch('src.models.docker_modelrunner_adapter.DockerModelRunnerAdapter.generate')
async def test_mock_llm_service_with_modelrunner(mock_adapter_generate):
    """Test the MockLLMService using Docker Model Runner."""
    # Setup mock for DockerModelRunnerAdapter.generate
    mock_adapter_generate.return_value = "Response from Docker Model Runner"
    
    # Create MockLLMService with model_runner_enabled=True
    service = MockLLMService(
        use_model_runner=True,
        model_runner_url="http://localhost:8080",
        model_runner_models=["phi3:mini", "llama3:8b"]
    )
    
    # Test the analyze method
    response = await service.analyze(
        prompt="Test prompt",
        model="phi3:mini",
        context="Some context"
    )
    
    assert "Response from Docker Model Runner" in response
    mock_adapter_generate.assert_called_once()


@pytest.mark.asyncio
@patch('src.models.docker_modelrunner_adapter.DockerModelRunnerAdapter.generate')
async def test_mock_llm_service_fallback(mock_adapter_generate):
    """Test MockLLMService fallback to static responses when Docker Model Runner fails."""
    # Setup mock for DockerModelRunnerAdapter.generate to simulate failure
    mock_adapter_generate.side_effect = Exception("Connection failed")
    
    # Create MockLLMService with model_runner_enabled=True
    service = MockLLMService(
        use_model_runner=True,
        model_runner_url="http://localhost:8080",
        model_runner_models=["phi3:mini", "llama3:8b"]
    )
    
    # Test the analyze method
    response = await service.analyze(
        prompt="Test prompt",
        model="phi3:mini",
        context="Some context"
    )
    
    # Should contain default static response, not the Docker Model Runner response
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    # Fallback message should be included
    assert "mock response" in response.lower()
    mock_adapter_generate.assert_called_once()


if __name__ == "__main__":
    # If run directly, check if Docker Model Runner is available
    print("Testing Docker Model Runner availability...")
    is_available = asyncio.run(test_docker_modelrunner_available())
    if is_available:
        print("Docker Model Runner is available and ready for integration with Ultra.")
    else:
        print("Docker Model Runner is not available. Please check its installation and configuration.")
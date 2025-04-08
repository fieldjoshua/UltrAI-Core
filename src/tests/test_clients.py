from unittest.mock import Mock, patch

import pytest

from ..clients import ChatGPTClient, GeminiClient, LlamaClient
from ..config import ModelConfig


@pytest.fixture
def model_config():
    return ModelConfig(
        api_key="test-key",
        max_tokens=100,
        temperature=0.7,
        timeout=30,
        base_url="http://test.endpoint",
    )


@pytest.mark.asyncio
async def test_chatgpt_client_init(model_config):
    async with ChatGPTClient(model_config) as client:
        assert client.config.api_key == "test-key"
        assert client.session is not None


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post")
async def test_chatgpt_generate(mock_post, model_config):
    # Mock the response
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test response"}}]
    }
    mock_post.return_value.__aenter__.return_value = mock_response

    async with ChatGPTClient(model_config) as client:
        response = await client.generate("test prompt")
        assert response == "test response"


# Similar tests for other clients...

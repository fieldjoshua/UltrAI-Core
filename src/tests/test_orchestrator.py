import asyncio
from unittest.mock import Mock, patch

import pytest

from ..config import Config
from ..models import ModelResponse, QualityMetrics
from ..orchestrator import TriLLMOrchestrator


@pytest.fixture
def config():
    return Config("tests/test_config.yaml")


@pytest.fixture
async def orchestrator(config):
    mock_llama = Mock()
    mock_chatgpt = Mock()
    mock_gemini = Mock()

    orchestrator = TriLLMOrchestrator(
        mock_llama, mock_chatgpt, mock_gemini, config.orchestrator
    )

    return orchestrator


@pytest.mark.asyncio
async def test_get_model_response(orchestrator):
    mock_model = Mock()
    mock_model.generate.return_value = "Test response"

    response = await orchestrator.get_model_response(mock_model, "Test prompt", "test")

    assert isinstance(response, ModelResponse)
    assert response.content == "Test response"
    assert response.stage == "test"


@pytest.mark.asyncio
async def test_process_responses_success(orchestrator):
    # Setup mock responses
    orchestrator.llama.generate.return_value = "Llama response"
    orchestrator.chatgpt.generate.return_value = "ChatGPT response"
    orchestrator.gemini.generate.return_value = "Gemini response"

    result = await orchestrator.process_responses("Test prompt")

    assert result["status"] == "success"
    assert len(result["initial_responses"]) == 3
    assert result["final_synthesis"] is not None

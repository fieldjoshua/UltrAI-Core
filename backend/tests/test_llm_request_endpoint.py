import pytest
from fastapi.testclient import TestClient
import os
import json
from unittest.mock import patch, MagicMock

from backend.app import app
from backend.config import Settings
from backend.models.llm_models import ModelProvider

client = TestClient(app)

# Test data
MOCK_LLM_RESPONSE = {
    "text": "This is a mock response from the LLM service.",
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 15,
        "total_tokens": 25
    }
}

# Sample request data
VALID_REQUEST = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "prompt": "Write a hello world program",
    "options": {
        "temperature": 0.7,
        "max_tokens": 100
    }
}

@pytest.fixture
def mock_env_vars():
    """Fixture to set and restore environment variables"""
    original_env = os.environ.copy()
    os.environ["MOCK_MODE"] = "false"
    os.environ["OPENAI_API_KEY"] = "test-openai-key"
    os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def mock_llm_service():
    """Fixture to mock the LLM service"""
    with patch('backend.services.llm_service.query_llm', return_value=MOCK_LLM_RESPONSE) as mock:
        yield mock

def test_llm_request_happy_path(mock_env_vars, mock_llm_service):
    """Test successful LLM request with valid inputs"""
    response = client.post("/api/llm-request", json=VALID_REQUEST)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "text" in data
    assert "usage" in data
    assert data["text"] == MOCK_LLM_RESPONSE["text"]
    
    # Verify mock was called with correct parameters
    mock_llm_service.assert_called_once()
    call_args = mock_llm_service.call_args[0]
    assert call_args[0] == VALID_REQUEST["provider"]
    assert call_args[1] == VALID_REQUEST["model"]
    assert call_args[2] == VALID_REQUEST["prompt"]

def test_llm_request_missing_fields():
    """Test request with missing required fields"""
    # Test missing provider
    invalid_request = VALID_REQUEST.copy()
    del invalid_request["provider"]
    response = client.post("/api/llm-request", json=invalid_request)
    assert response.status_code == 422
    
    # Test missing model
    invalid_request = VALID_REQUEST.copy()
    del invalid_request["model"]
    response = client.post("/api/llm-request", json=invalid_request)
    assert response.status_code == 422
    
    # Test missing prompt
    invalid_request = VALID_REQUEST.copy()
    del invalid_request["prompt"]
    response = client.post("/api/llm-request", json=invalid_request)
    assert response.status_code == 422

def test_llm_request_invalid_provider(mock_env_vars):
    """Test request with invalid provider"""
    invalid_request = VALID_REQUEST.copy()
    invalid_request["provider"] = "nonexistent-provider"
    
    response = client.post("/api/llm-request", json=invalid_request)
    
    assert response.status_code == 400
    assert "error" in response.json()
    assert "provider" in response.json()["error"].lower()

def test_llm_request_invalid_model(mock_env_vars):
    """Test request with invalid model for provider"""
    invalid_request = VALID_REQUEST.copy()
    invalid_request["model"] = "nonexistent-model"
    
    response = client.post("/api/llm-request", json=invalid_request)
    
    assert response.status_code == 400
    assert "error" in response.json()
    assert "model" in response.json()["error"].lower()

def test_llm_request_service_error(mock_env_vars):
    """Test handling of service errors"""
    
    # Mock a service error
    with patch('backend.services.llm_service.query_llm', 
               side_effect=Exception("Service error")):
        response = client.post("/api/llm-request", json=VALID_REQUEST)
        
        assert response.status_code == 500
        assert "error" in response.json()

def test_llm_request_rate_limit_error(mock_env_vars):
    """Test handling of rate limit errors"""
    
    # Mock a rate limit error
    with patch('backend.services.llm_service.query_llm', 
               side_effect=Exception("Rate limit exceeded")):
        response = client.post("/api/llm-request", json=VALID_REQUEST)
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        # If your application has special handling for rate limits, test that here
        # assert "rate limit" in data["error"].lower()

def test_llm_request_empty_prompt(mock_env_vars):
    """Test request with empty prompt"""
    invalid_request = VALID_REQUEST.copy()
    invalid_request["prompt"] = ""
    
    response = client.post("/api/llm-request", json=invalid_request)
    
    # Assuming your API validates prompt length
    assert response.status_code == 400
    assert "error" in response.json()
    assert "prompt" in response.json()["error"].lower()

def test_llm_request_large_prompt(mock_env_vars, mock_llm_service):
    """Test handling of large prompts"""
    large_request = VALID_REQUEST.copy()
    large_request["prompt"] = "A" * 10000  # 10K characters
    
    response = client.post("/api/llm-request", json=large_request)
    
    # If your API handles large prompts, this should succeed
    assert response.status_code == 200
    
    # If your API truncates or rejects large prompts, test that behavior instead
    # assert response.status_code == 400
    # assert "too large" in response.json()["error"].lower()

def test_llm_request_in_mock_mode():
    """Test LLM request in mock mode"""
    with patch.dict(os.environ, {"MOCK_MODE": "true"}):
        response = client.post("/api/llm-request", json=VALID_REQUEST)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for mock response indicators
        assert "text" in data
        # In mock mode, the response should contain some indication it's mocked
        assert data["text"] is not None and len(data["text"]) > 0
        assert "usage" in data

def test_llm_request_custom_options(mock_env_vars, mock_llm_service):
    """Test LLM request with custom options"""
    custom_request = VALID_REQUEST.copy()
    custom_request["options"] = {
        "temperature": 0.9,
        "max_tokens": 500,
        "top_p": 0.95,
        "frequency_penalty": 0.5
    }
    
    response = client.post("/api/llm-request", json=custom_request)
    
    assert response.status_code == 200
    
    # Verify options were passed to the service
    kwargs = mock_llm_service.call_args[1]
    assert "options" in kwargs
    assert kwargs["options"]["temperature"] == 0.9
    assert kwargs["options"]["max_tokens"] == 500

if __name__ == "__main__":
    pytest.main(["-xvs", "test_llm_request_endpoint.py"])
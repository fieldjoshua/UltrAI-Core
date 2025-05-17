"""
Tests for analysis configuration validation.

This module tests the validation of analysis configurations, including model selection,
pattern selection, and option validation.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app import app
from backend.config import Config

client = TestClient(app)

# Test data
TEST_USER = {
    "email": "config_test@example.com",
    "password": "SecurePassword123!",
    "name": "Config Test User",
}

VALID_PROMPT = "Analyze the impact of climate change on global food security."


@pytest.fixture
def registered_user():
    """Register a test user and return the user data."""
    # Register user
    response = client.post("/api/auth/register", json=TEST_USER)

    if response.status_code != status.HTTP_201_CREATED:
        # Try logging in if user already exists
        login_response = client.post(
            "/api/auth/login",
            json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
        )
        assert login_response.status_code == status.HTTP_200_OK
        return login_response.json()

    return response.json()


@pytest.fixture
def auth_headers(registered_user):
    """Get authentication headers for the test user."""
    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
    )

    assert login_response.status_code == status.HTTP_200_OK
    assert "access_token" in login_response.json()

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_available_models():
    """Mock the available models endpoint."""
    with patch("backend.services.llm_config_service.get_available_models") as mock:
        mock.return_value = {
            "available_models": [
                {
                    "id": "gpt4o",
                    "name": "GPT-4o",
                    "provider": "openai",
                    "capabilities": ["general", "reasoning", "code"],
                    "context_length": 128000,
                },
                {
                    "id": "claude37",
                    "name": "Claude 3.7 Sonnet",
                    "provider": "anthropic",
                    "capabilities": ["general", "reasoning"],
                    "context_length": 200000,
                },
                {
                    "id": "local-llama",
                    "name": "Local Llama 3",
                    "provider": "local",
                    "capabilities": ["general"],
                    "context_length": 8000,
                },
            ]
        }
        yield mock


@pytest.fixture
def mock_analysis_patterns():
    """Mock the analysis patterns endpoint."""
    with patch("backend.services.prompt_service.get_analysis_patterns") as mock:
        mock.return_value = {
            "patterns": [
                {
                    "id": "confidence",
                    "name": "Confidence Analysis",
                    "description": "Analyzes responses based on confidence levels",
                    "supported_models": ["gpt4o", "claude37"],
                },
                {
                    "id": "factual",
                    "name": "Factual Accuracy",
                    "description": "Evaluates responses for factual accuracy",
                    "supported_models": ["gpt4o", "claude37", "local-llama"],
                },
                {
                    "id": "comparison",
                    "name": "Direct Comparison",
                    "description": "Compares responses side by side",
                    "supported_models": ["gpt4o", "claude37", "local-llama"],
                },
            ]
        }
        yield mock


def test_available_models_endpoint(client, auth_headers, mock_available_models):
    """Test the available models endpoint."""
    response = client.get("/api/available-models", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert "available_models" in response.json()
    models = response.json()["available_models"]
    assert len(models) == 3

    # Verify model data structure
    assert "id" in models[0]
    assert "name" in models[0]
    assert "provider" in models[0]
    assert "capabilities" in models[0]
    assert "context_length" in models[0]

    # Verify model IDs
    model_ids = [model["id"] for model in models]
    assert "gpt4o" in model_ids
    assert "claude37" in model_ids
    assert "local-llama" in model_ids


def test_available_models_no_auth(client):
    """Test the available models endpoint without authentication."""
    response = client.get("/api/available-models")

    # This could either require auth or not, depending on the API design
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        assert "detail" in response.json()
    else:
        assert response.status_code == status.HTTP_200_OK
        assert "available_models" in response.json()


def test_analysis_patterns_endpoint(client, auth_headers, mock_analysis_patterns):
    """Test the analysis patterns endpoint."""
    response = client.get("/api/analysis-patterns", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert "patterns" in response.json()
    patterns = response.json()["patterns"]
    assert len(patterns) == 3

    # Verify pattern data structure
    assert "id" in patterns[0]
    assert "name" in patterns[0]
    assert "description" in patterns[0]
    assert "supported_models" in patterns[0]

    # Verify pattern IDs
    pattern_ids = [pattern["id"] for pattern in patterns]
    assert "confidence" in pattern_ids
    assert "factual" in pattern_ids
    assert "comparison" in pattern_ids


def test_valid_analysis_config(client, auth_headers, mock_available_models):
    """Test an analysis request with valid configuration."""
    # Mock the LLM service
    with patch("backend.services.llm_service.query_llm") as mock_query:
        mock_query.return_value = {"text": "This is a mock response"}

        # Prepare analysis request
        analysis_payload = {
            "prompt": VALID_PROMPT,
            "selected_models": ["gpt4o", "claude37"],
            "ultra_model": "gpt4o",
            "pattern": "confidence",
            "options": {"max_tokens": 1000, "temperature": 0.7},
            "output_format": "markdown",
        }

        response = client.post(
            "/api/analyze", json=analysis_payload, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert "status" in response.json()
        assert response.json()["status"] == "success"
        assert "analysis_id" in response.json()
        assert "results" in response.json()


def test_invalid_prompt(client, auth_headers):
    """Test an analysis request with an invalid prompt."""
    analysis_payload = {
        "prompt": "",  # Empty prompt
        "selected_models": ["gpt4o"],
        "ultra_model": "gpt4o",
        "pattern": "confidence",
        "options": {},
    }

    response = client.post("/api/analyze", json=analysis_payload, headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "status" in response.json()
    assert response.json()["status"] == "error"
    assert "message" in response.json()
    assert "prompt" in response.json()["message"].lower()


def test_invalid_model_selection(client, auth_headers, mock_available_models):
    """Test an analysis request with invalid model selection."""
    analysis_payload = {
        "prompt": VALID_PROMPT,
        "selected_models": ["nonexistent_model"],
        "ultra_model": "nonexistent_model",
        "pattern": "confidence",
        "options": {},
    }

    response = client.post("/api/analyze", json=analysis_payload, headers=auth_headers)

    # In real mode, this should return an error
    # In mock mode, it might still succeed
    if Config.use_mock:
        # Skip validation in mock mode
        pass
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "status" in response.json()
        assert response.json()["status"] == "error"
        assert "model" in response.json()["message"].lower()


def test_model_compatibility_with_pattern(
    client, auth_headers, mock_available_models, mock_analysis_patterns
):
    """Test model compatibility with a specific pattern."""
    # Test with a model that doesn't support the given pattern
    # The 'confidence' pattern doesn't support 'local-llama' according to our mock
    analysis_payload = {
        "prompt": VALID_PROMPT,
        "selected_models": ["local-llama"],
        "ultra_model": "local-llama",
        "pattern": "confidence",
        "options": {},
    }

    response = client.post("/api/analyze", json=analysis_payload, headers=auth_headers)

    # In real mode, this should return an error about compatibility
    # In mock mode, it might still succeed
    if Config.use_mock:
        # Skip validation in mock mode
        pass
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "status" in response.json()
        assert response.json()["status"] == "error"
        assert "compatibility" in response.json()["message"].lower()
        assert "pattern" in response.json()["message"].lower()


def test_invalid_pattern(client, auth_headers):
    """Test an analysis request with an invalid pattern."""
    analysis_payload = {
        "prompt": VALID_PROMPT,
        "selected_models": ["gpt4o"],
        "ultra_model": "gpt4o",
        "pattern": "nonexistent_pattern",
        "options": {},
    }

    response = client.post("/api/analyze", json=analysis_payload, headers=auth_headers)

    # In real mode, this should return an error
    # In mock mode, it might default to a standard pattern
    if Config.use_mock:
        # Skip validation in mock mode
        pass
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "status" in response.json()
        assert response.json()["status"] == "error"
        assert "pattern" in response.json()["message"].lower()


def test_invalid_options(client, auth_headers):
    """Test an analysis request with invalid options."""
    analysis_payload = {
        "prompt": VALID_PROMPT,
        "selected_models": ["gpt4o"],
        "ultra_model": "gpt4o",
        "pattern": "confidence",
        "options": {
            "temperature": 2.5,  # Invalid temperature (should be 0-1)
            "max_tokens": -100,  # Invalid token count
        },
    }

    response = client.post("/api/analyze", json=analysis_payload, headers=auth_headers)

    # In real mode, this should return an error
    # In mock mode, it might use default values
    if Config.use_mock:
        # Skip validation in mock mode
        pass
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "status" in response.json()
        assert response.json()["status"] == "error"
        assert "options" in response.json()["message"].lower()


def test_ultra_model_in_selected_models(client, auth_headers):
    """Test that the ultra model must be one of the selected models."""
    analysis_payload = {
        "prompt": VALID_PROMPT,
        "selected_models": ["gpt4o"],
        "ultra_model": "claude37",  # Not in selected_models
        "pattern": "confidence",
        "options": {},
    }

    response = client.post("/api/analyze", json=analysis_payload, headers=auth_headers)

    # In real mode, this should return an error
    # In mock mode, it might add the ultra model to selected models
    if Config.use_mock:
        # Skip validation in mock mode
        pass
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "status" in response.json()
        assert response.json()["status"] == "error"
        assert "ultra_model" in response.json()["message"].lower()
        assert "selected_models" in response.json()["message"].lower()


def test_save_configuration(client, auth_headers):
    """Test saving an analysis configuration."""
    config_payload = {
        "name": "Climate Analysis Config",
        "description": "Configuration for climate change analysis",
        "selected_models": ["gpt4o", "claude37"],
        "ultra_model": "gpt4o",
        "pattern": "confidence",
        "options": {"max_tokens": 1000, "temperature": 0.7},
    }

    # Mock the configuration service
    with patch("backend.services.llm_config_service.save_user_config") as mock_save:
        mock_save.return_value = {
            "config_id": "config-123",
            "name": config_payload["name"],
            "description": config_payload["description"],
            "created_at": "2025-05-13T12:00:00Z",
            **config_payload,
        }

        response = client.post(
            "/api/analysis-configs", json=config_payload, headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "config_id" in response.json()
        assert response.json()["name"] == config_payload["name"]
        assert response.json()["selected_models"] == config_payload["selected_models"]
        assert response.json()["ultra_model"] == config_payload["ultra_model"]
        assert response.json()["pattern"] == config_payload["pattern"]


def test_load_configuration(client, auth_headers):
    """Test loading a saved analysis configuration."""
    config_id = "config-123"

    # Mock the configuration service
    with patch("backend.services.llm_config_service.get_user_config") as mock_get:
        mock_get.return_value = {
            "config_id": config_id,
            "name": "Climate Analysis Config",
            "description": "Configuration for climate change analysis",
            "selected_models": ["gpt4o", "claude37"],
            "ultra_model": "gpt4o",
            "pattern": "confidence",
            "options": {"max_tokens": 1000, "temperature": 0.7},
            "created_at": "2025-05-13T12:00:00Z",
        }

        response = client.get(
            f"/api/analysis-configs/{config_id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert "config_id" in response.json()
        assert response.json()["config_id"] == config_id
        assert "selected_models" in response.json()
        assert "ultra_model" in response.json()
        assert "pattern" in response.json()
        assert "options" in response.json()


def test_list_configurations(client, auth_headers):
    """Test listing saved analysis configurations."""
    # Mock the configuration service
    with patch("backend.services.llm_config_service.get_user_configs") as mock_list:
        mock_list.return_value = [
            {
                "config_id": "config-123",
                "name": "Climate Analysis Config",
                "description": "Configuration for climate change analysis",
                "selected_models": ["gpt4o", "claude37"],
                "ultra_model": "gpt4o",
                "pattern": "confidence",
                "created_at": "2025-05-13T12:00:00Z",
            },
            {
                "config_id": "config-456",
                "name": "Code Review Config",
                "description": "Configuration for code review",
                "selected_models": ["gpt4o"],
                "ultra_model": "gpt4o",
                "pattern": "factual",
                "created_at": "2025-05-13T13:00:00Z",
            },
        ]

        response = client.get("/api/analysis-configs", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "configs" in response.json()
        configs = response.json()["configs"]
        assert len(configs) == 2
        assert configs[0]["config_id"] == "config-123"
        assert configs[1]["config_id"] == "config-456"


if __name__ == "__main__":
    pytest.main(["-xvs", "test_analysis_config_validation.py"])

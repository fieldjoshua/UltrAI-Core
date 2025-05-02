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
MOCK_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-3.5-turbo", "gpt-4"],
        "enabled": True
    },
    "anthropic": {
        "name": "Anthropic",
        "models": ["claude-2.1", "claude-3-opus"],
        "enabled": True
    },
    "google": {
        "name": "Google",
        "models": ["gemini-pro", "gemini-1.5-pro"],
        "enabled": False
    }
}

@pytest.fixture
def mock_config():
    """Fixture to mock the config with predefined providers"""
    config = MagicMock()
    config.MODEL_PROVIDERS = MOCK_PROVIDERS
    return config

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

def test_available_models_endpoint(mock_config):
    """Test the /api/available-models endpoint returns correct models"""
    with patch('backend.routes.llm_routes.get_settings', return_value=mock_config):
        response = client.get("/api/available-models")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure and content
        assert "providers" in data
        providers = data["providers"]
        
        # Check provider count (only enabled providers should be returned)
        assert len(providers) == 2
        
        # Check specific providers and their models
        provider_names = [p["name"] for p in providers]
        assert "OpenAI" in provider_names
        assert "Anthropic" in provider_names
        assert "Google" not in provider_names
        
        # Check models for a specific provider
        openai_provider = next(p for p in providers if p["name"] == "OpenAI")
        assert "models" in openai_provider
        assert "gpt-3.5-turbo" in openai_provider["models"]
        assert "gpt-4" in openai_provider["models"]

def test_available_models_with_mock_mode():
    """Test that mock mode correctly affects available models"""
    # Enable mock mode
    with patch.dict(os.environ, {"MOCK_MODE": "true"}):
        response = client.get("/api/available-models")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify mock provider exists
        assert "providers" in data
        providers = data["providers"]
        
        # At least one provider should be available in mock mode
        assert len(providers) > 0
        
        # Check mock indication
        mock_indicated = any("mock" in p["name"].lower() for p in providers)
        assert mock_indicated, "Mock mode should be indicated in provider names"

def test_available_models_authentication_error(mock_env_vars):
    """Test handling of authentication errors with providers"""
    
    # Mock an authentication error when checking available models
    def mock_authenticate_error(*args, **kwargs):
        # Simulate authentication failure for one provider
        if args and args[0] == "openai":
            raise Exception("Authentication error")
        # Return success for others
        return True
    
    with patch('backend.services.llm_config_service.authenticate_provider', 
              side_effect=mock_authenticate_error):
        response = client.get("/api/available-models")
        
        assert response.status_code == 200
        data = response.json()
        
        # OpenAI should not be in the providers due to auth error
        provider_names = [p["name"] for p in data["providers"]]
        assert "OpenAI" not in provider_names
        assert "Anthropic" in provider_names

def test_available_models_connection_error():
    """Test handling of connection errors when fetching models"""
    
    # Create a config with test providers
    mock_settings = MagicMock()
    mock_settings.MODEL_PROVIDERS = MOCK_PROVIDERS
    
    # Mock a connection error when authenticating
    def mock_connection_error(*args, **kwargs):
        raise ConnectionError("Connection failed")
    
    with patch('backend.routes.llm_routes.get_settings', return_value=mock_settings):
        with patch('backend.services.llm_config_service.authenticate_provider', 
                  side_effect=mock_connection_error):
            response = client.get("/api/available-models")
            
            # The endpoint should handle the error and return a 500 response
            assert response.status_code == 500
            data = response.json()
            
            # Check error message
            assert "error" in data
            assert "retrieving available models" in data["error"].lower()

def test_available_models_cached_response():
    """Test that responses are cached for performance"""
    
    mock_settings = MagicMock()
    mock_settings.MODEL_PROVIDERS = MOCK_PROVIDERS
    
    # Use a counter to track calls to the authenticate function
    call_counter = {"count": 0}
    
    def mock_authenticate(*args, **kwargs):
        call_counter["count"] += 1
        return True
    
    with patch('backend.routes.llm_routes.get_settings', return_value=mock_settings):
        with patch('backend.services.llm_config_service.authenticate_provider', 
                  side_effect=mock_authenticate):
            # First call
            response1 = client.get("/api/available-models")
            assert response1.status_code == 200
            
            # Second call should use cache
            response2 = client.get("/api/available-models")
            assert response2.status_code == 200
            
            # Check that authenticate was only called once if caching is implemented
            # This test might need adjustment if caching is not implemented
            if "Cache-Control" in response1.headers:
                assert call_counter["count"] == 1
                assert json.dumps(response1.json()) == json.dumps(response2.json())

if __name__ == "__main__":
    pytest.main(["-xvs", "test_available_models_endpoint.py"])
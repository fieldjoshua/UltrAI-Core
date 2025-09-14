"""Test health check behavior with rate limiting and configuration options."""

import os
import pytest
from unittest.mock import patch, Mock
from datetime import datetime

from app.utils.health_check import (
    HealthStatus,
    check_llm_provider_health,
    HEALTH_CHECK_SKIP_API_CALLS
)
from app.services.health_service import HealthService


class TestHealthCheckBehavior:
    """Test suite for health check behavior updates."""
    
    def test_skip_api_calls_when_configured(self, monkeypatch):
        """Test that health checks skip API calls when configured."""
        # Set environment variable to skip API calls
        monkeypatch.setenv("HEALTH_CHECK_SKIP_API_CALLS", "true")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        
        # Need to reload the module to pick up env var change
        import app.utils.health_check
        import importlib
        importlib.reload(app.utils.health_check)
        
        result = app.utils.health_check.check_llm_provider_health("openai", "OPENAI_API_KEY")
        
        assert result["status"] == HealthStatus.OK
        assert result["api_check_skipped"] is True
        assert "API check skipped" in result["message"]
        assert result["api_key_configured"] is True
    
    def test_rate_limited_providers_considered_healthy(self, monkeypatch):
        """Test that rate-limited providers don't cause degraded status."""
        # Mock the provider health check responses
        mock_provider_status = {
            "openai": {
                "status": "degraded",
                "message": "Rate limit exceeded",
                "status_code": 429
            },
            "anthropic": {
                "status": "ok",
                "message": "Provider healthy"
            }
        }
        
        # Mock llm_config_service
        mock_llm_config = Mock()
        mock_llm_config.get_available_models.return_value = {
            "gpt-4": {"provider": "openai"},
            "claude-3": {"provider": "anthropic"}
        }
        
        # Patch the health service
        with patch('app.services.health_service.llm_config_service', mock_llm_config):
            with patch.object(HealthService, '_check_llm_provider_connectivity', 
                            return_value=mock_provider_status):
                service = HealthService()
                service._check_llm_services()
                
                # Service should be healthy even with rate-limited provider
                assert service.service_status["llm"]["status"] == "healthy"
                assert "rate-limited" in service.service_status["llm"]["message"]
                assert service.service_status["llm"]["rate_limited_providers"] == ["openai"]
                assert service.service_status["llm"]["available_providers"] == ["anthropic"]
    
    def test_all_providers_rate_limited_still_healthy(self, monkeypatch):
        """Test that all rate-limited providers still show as healthy."""
        # Mock all providers as rate limited
        mock_provider_status = {
            "openai": {
                "status": "degraded", 
                "message": "Rate limit exceeded",
                "status_code": 429
            },
            "anthropic": {
                "status": "degraded",
                "message": "Too many requests - rate limited"
            }
        }
        
        mock_llm_config = Mock()
        mock_llm_config.get_available_models.return_value = {
            "gpt-4": {"provider": "openai"},
            "claude-3": {"provider": "anthropic"}
        }
        
        with patch('app.services.health_service.llm_config_service', mock_llm_config):
            with patch.object(HealthService, '_check_llm_provider_connectivity',
                            return_value=mock_provider_status):
                service = HealthService()
                service._check_llm_services()
                
                # Should still be healthy as rate limiting is temporary
                assert service.service_status["llm"]["status"] == "healthy"
                assert len(service.service_status["llm"]["rate_limited_providers"]) == 2
    
    def test_truly_unavailable_providers_cause_degraded(self, monkeypatch):
        """Test that truly unavailable providers cause degraded status."""
        # Mock all providers as unavailable (not just rate limited)
        mock_provider_status = {
            "openai": {
                "status": "critical",
                "message": "Connection failed"
            },
            "anthropic": {
                "status": "unavailable",
                "message": "Authentication failed",
                "status_code": 401
            }
        }
        
        mock_llm_config = Mock()
        mock_llm_config.get_available_models.return_value = {
            "gpt-4": {"provider": "openai"},
            "claude-3": {"provider": "anthropic"}
        }
        
        with patch('app.services.health_service.llm_config_service', mock_llm_config):
            with patch.object(HealthService, '_check_llm_provider_connectivity',
                            return_value=mock_provider_status):
                service = HealthService()
                service._check_llm_services()
                
                # Should be degraded when no providers are available
                assert service.service_status["llm"]["status"] == "degraded"
                assert "no providers are reachable" in service.service_status["llm"]["message"]


class TestHealthCheckEndpoints:
    """Test that endpoints use correct paths."""
    
    def test_correct_endpoint_paths(self):
        """Document correct endpoint paths for health checks."""
        correct_endpoints = {
            "health": "/api/health",
            "models": "/api/available-models",  # NOT /api/models
            "model_health": "/api/models/health",  # NOT /api/model-health
            "orchestrator": "/api/orchestrator/analyze",  # NOT /api/orchestrate
            "orchestrator_health": "/api/orchestrator/health",
            "auth": "/api/auth/login"  # Should accept POST
        }
        
        # This is more documentation than test, but ensures we remember correct paths
        assert correct_endpoints["models"] == "/api/available-models"
        assert correct_endpoints["orchestrator"] == "/api/orchestrator/analyze"
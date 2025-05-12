"""
Tests for health check endpoints.

These tests verify that the health check endpoints return the expected results and
properly report the health status of various services.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.app import app
from backend.utils.health_check import HealthStatus, ServiceType, health_check_registry

# Create test client
client = TestClient(app)


def test_basic_health_endpoint():
    """Test that the basic health endpoint returns a valid response."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] in [
        HealthStatus.OK, 
        HealthStatus.DEGRADED,
        HealthStatus.CRITICAL,
        HealthStatus.UNAVAILABLE
    ]
    assert "uptime" in data
    assert isinstance(data["uptime"], int)


def test_api_health_endpoint():
    """Test that the API health endpoint returns a valid response."""
    response = client.get("/api/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "api_version" in data
    assert "environment" in data
    assert "instance_id" in data
    assert "uptime" in data


def test_api_health_endpoint_with_detail():
    """Test that the API health endpoint returns detailed information when requested."""
    response = client.get("/api/health?detail=true")
    assert response.status_code == 200
    
    data = response.json()
    assert "services" in data
    assert "dependencies" in data
    assert "features" in data
    
    # Check that services include some expected ones
    services = data["services"]
    assert "database" in services
    assert "redis" in services
    assert "system" in services
    
    # Verify service structure
    for service_name, service_data in services.items():
        assert "status" in service_data
        assert service_data["status"] in [
            HealthStatus.OK, 
            HealthStatus.DEGRADED,
            HealthStatus.CRITICAL,
            HealthStatus.UNAVAILABLE,
            HealthStatus.UNKNOWN
        ]


def test_api_health_endpoint_with_system_metrics():
    """Test that the API health endpoint includes system metrics when requested."""
    response = client.get("/api/health?include_system=true")
    assert response.status_code == 200
    
    data = response.json()
    assert "system" in data
    
    system = data["system"]
    assert "memory" in system
    assert "disk" in system
    assert "requests" in system


def test_api_health_endpoint_with_specific_service():
    """Test that the API health endpoint can check a specific service."""
    response = client.get("/api/health?service=system")
    assert response.status_code == 200
    
    data = response.json()
    assert "service" in data
    assert data["service"] == "system"
    assert "status" in data
    assert "details" in data


def test_api_health_endpoint_with_invalid_service():
    """Test that the API health endpoint returns 404 for invalid service."""
    response = client.get("/api/health?service=nonexistent")
    assert response.status_code == 404
    
    data = response.json()
    assert "error" in data


def test_api_health_endpoint_with_service_type():
    """Test that the API health endpoint can filter by service type."""
    response = client.get("/api/health?type=system")
    assert response.status_code == 200
    
    data = response.json()
    assert "service_type" in data
    assert data["service_type"] == "system"
    assert "services" in data
    assert "system" in data["services"]


def test_api_health_endpoint_with_invalid_service_type():
    """Test that the API health endpoint returns 400 for invalid service type."""
    response = client.get("/api/health?type=nonexistent")
    assert response.status_code == 400
    
    data = response.json()
    assert "error" in data


def test_system_health_endpoint():
    """Test that the system health endpoint returns valid information."""
    response = client.get("/api/health/system")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "details" in data
    
    details = data["details"]
    assert "memory" in details
    assert "disk" in details
    assert "cpu" in details


def test_dependencies_health_endpoint():
    """Test that the dependencies health endpoint returns valid information."""
    response = client.get("/api/health/dependencies")
    assert response.status_code == 200
    
    data = response.json()
    assert "dependencies" in data
    assert "features" in data
    assert "all_required_available" in data
    assert isinstance(data["all_required_available"], bool)


def test_services_health_endpoint():
    """Test that the services health endpoint returns valid information."""
    response = client.get("/api/health/services")
    assert response.status_code == 200
    
    data = response.json()
    assert "services" in data
    
    services = data["services"]
    assert len(services) > 0


def test_services_health_endpoint_with_service_type():
    """Test that the services health endpoint can filter by service type."""
    response = client.get("/api/health/services?service_type=llm_provider")
    assert response.status_code == 200
    
    data = response.json()
    assert "service_type" in data
    assert data["service_type"] == "llm_provider"
    assert "services" in data
    
    services = data["services"]
    assert "openai" in services
    assert "anthropic" in services
    assert "google" in services


def test_services_health_endpoint_with_invalid_service_type():
    """Test that the services health endpoint returns 400 for invalid service type."""
    response = client.get("/api/health/services?service_type=nonexistent")
    assert response.status_code == 400
    
    data = response.json()
    assert "error" in data


def test_llm_health_endpoint():
    """Test that the LLM health endpoint returns valid information."""
    response = client.get("/api/health/llm")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "providers" in data
    
    providers = data["providers"]
    assert "openai" in providers
    assert "anthropic" in providers
    assert "google" in providers


def test_llm_health_endpoint_with_provider():
    """Test that the LLM health endpoint can check a specific provider."""
    response = client.get("/api/health/llm?provider=openai")
    assert response.status_code == 200
    
    data = response.json()
    assert "provider" in data
    assert data["provider"] == "openai"
    assert "status" in data
    assert "details" in data


def test_llm_health_endpoint_with_invalid_provider():
    """Test that the LLM health endpoint returns 404 for invalid provider."""
    response = client.get("/api/health/llm?provider=nonexistent")
    assert response.status_code == 404
    
    data = response.json()
    assert "error" in data


def test_ping_endpoint():
    """Test that the ping endpoint returns pong."""
    response = client.get("/ping")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert data["message"] == "pong"


def test_info_endpoint():
    """Test that the info endpoint returns valid information."""
    response = client.get("/info")
    assert response.status_code == 200
    
    data = response.json()
    assert "api_version" in data
    assert "environment" in data
    assert "platform" in data
    assert "python_version" in data
    assert "hostname" in data


@patch("backend.utils.health_check.check_database_health")
def test_database_health_critical(mock_db_health):
    """Test that database health critical status is reported correctly."""
    # Mock database health to return critical status
    mock_db_health.return_value = {
        "status": HealthStatus.CRITICAL,
        "message": "Database connection failed",
        "details": {"connected": False},
        "timestamp": "2025-05-01T12:00:00Z",
    }
    
    response = client.get("/api/health?detail=true")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == HealthStatus.CRITICAL
    assert "services" in data
    assert "database" in data["services"]
    assert data["services"]["database"]["status"] == HealthStatus.CRITICAL


@patch("backend.utils.health_check.check_redis_health")
def test_redis_health_degraded(mock_redis_health):
    """Test that redis health degraded status is reported correctly."""
    # Mock redis health to return degraded status
    mock_redis_health.return_value = {
        "status": HealthStatus.DEGRADED,
        "message": "Redis not available, using in-memory cache",
        "details": {"using_fallback": True},
        "timestamp": "2025-05-01T12:00:00Z",
    }
    
    response = client.get("/api/health?detail=true")
    
    data = response.json()
    assert "services" in data
    assert "redis" in data["services"]
    assert data["services"]["redis"]["status"] == HealthStatus.DEGRADED


@patch("backend.utils.health_check.check_llm_provider_health")
def test_llm_provider_unavailable(mock_llm_health):
    """Test that LLM provider unavailable status is reported correctly."""
    # Mock LLM provider health to return unavailable status
    mock_llm_health.return_value = {
        "status": HealthStatus.UNAVAILABLE,
        "message": "OpenAI API connection failed",
        "provider": "openai",
        "error": "Connection error",
        "timestamp": "2025-05-01T12:00:00Z",
    }
    
    response = client.get("/api/health/llm?provider=openai")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == HealthStatus.UNAVAILABLE
    assert data["details"]["status"] == HealthStatus.UNAVAILABLE
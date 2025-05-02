import pytest
from fastapi.testclient import TestClient
import os
import json
from unittest.mock import patch, MagicMock

from backend.app import app

client = TestClient(app)

def test_health_endpoint_basic():
    """Test the basic health endpoint returns 200 OK"""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check for required fields
    assert "status" in data
    assert data["status"] == "ok"
    assert "version" in data

def test_health_endpoint_with_detail():
    """Test the health endpoint with detail parameter"""
    response = client.get("/api/health?detail=true")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check for detailed health info
    assert "status" in data
    assert "version" in data
    assert "services" in data
    
    # Verify services information
    services = data["services"]
    assert isinstance(services, dict)
    
    # Expected services might include database, cache, etc.
    # The actual services depend on your application
    expected_keys = ["database", "api_providers"]
    for key in expected_keys:
        if key in services:
            assert "status" in services[key]

def test_health_database_connection():
    """Test health endpoint correctly reports database status"""
    
    # Mock a database connection failure
    def mock_db_error(*args, **kwargs):
        raise Exception("Database connection error")
    
    with patch('backend.services.database_service.check_connection', 
               side_effect=mock_db_error):
        response = client.get("/api/health?detail=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # Overall status might still be ok if db is optional
        assert "services" in data
        if "database" in data["services"]:
            assert data["services"]["database"]["status"] == "error"

def test_health_endpoint_in_mock_mode():
    """Test health endpoint in mock mode"""
    with patch.dict(os.environ, {"MOCK_MODE": "true"}):
        response = client.get("/api/health?detail=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check mock mode is reported
        assert "mock_mode" in data
        assert data["mock_mode"] is True
        
        # API providers should report as mocked if included
        if "services" in data and "api_providers" in data["services"]:
            api_status = data["services"]["api_providers"]
            assert "mock" in json.dumps(api_status).lower()

def test_health_endpoint_when_degraded():
    """Test health endpoint correctly reflects degraded service state"""
    
    # Mock a partially degraded service state
    # This will depend on your health check implementation
    with patch('backend.services.health_service.get_service_status', 
               return_value={"status": "degraded", "message": "Service running at reduced capacity"}):
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "degraded"
        assert "message" in data

def test_health_endpoint_includes_environment():
    """Test health endpoint includes environment information"""
    # Set a specific environment variable
    with patch.dict(os.environ, {"ENVIRONMENT": "testing"}):
        response = client.get("/api/health?detail=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # Environment should be included in detailed output
        assert "environment" in data
        assert data["environment"] == "testing"

if __name__ == "__main__":
    pytest.main(["-xvs", "test_health_endpoint.py"])
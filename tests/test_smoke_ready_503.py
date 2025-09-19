"""
Smoke tests for READY/503 states in the orchestration service.

These tests verify:
1. Service returns 503 when insufficient models
2. Service returns READY when Big 3 providers are available
3. 503 payloads include required fields
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from app.routes.orchestrator_minimal import create_router
from app.services.orchestration_service import OrchestrationService


@pytest.mark.asyncio
async def test_service_status_insufficient_models():
    """Test that status endpoint shows unavailable when insufficient models."""
    # Create mock app with orchestration service
    app_mock = Mock()
    app_mock.state.orchestration_service = OrchestrationService(
        model_registry=Mock(),
        rate_limiter=Mock()
    )
    
    # Mock to return only 1 model when 3 are required
    app_mock.state.orchestration_service._default_models_from_env = AsyncMock(
        return_value=["gpt-4"]
    )
    
    # Create request mock
    request_mock = Mock()
    request_mock.app = app_mock
    
    # Get router and call status endpoint
    router = create_router()
    status_func = None
    for route in router.routes:
        if route.path == "/orchestrator/status":
            status_func = route.endpoint
            break
    
    result = await status_func(request_mock)
    
    # Verify response
    assert result["status"] == "unavailable"
    assert result["service_available"] is False
    assert "Insufficient" in result["message"] or "available" in result["message"]
    assert result["models"]["count"] == 1
    assert result["models"]["required"] == 3
    assert result["ready"] is False


@pytest.mark.asyncio
async def test_service_status_ready_with_big3():
    """Test that status endpoint shows ready when Big 3 providers available."""
    # Create mock app with orchestration service
    app_mock = Mock()
    app_mock.state.orchestration_service = OrchestrationService(
        model_registry=Mock(),
        rate_limiter=Mock()
    )
    
    # Mock to return all Big 3 providers
    app_mock.state.orchestration_service._default_models_from_env = AsyncMock(
        return_value=["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
    )
    
    # Create request mock
    request_mock = Mock()
    request_mock.app = app_mock
    
    # Get router and call status endpoint
    router = create_router()
    status_func = None
    for route in router.routes:
        if route.path == "/orchestrator/status":
            status_func = route.endpoint
            break
    
    result = await status_func(request_mock)
    
    # Verify response
    assert result["status"] == "healthy"
    assert result["service_available"] is True
    assert "Service operational with 3 models" in result["message"]
    assert result["models"]["count"] == 3
    assert set(result["models"]["providers_present"]) == {"openai", "anthropic", "google"}
    assert result["ready"] is True


@pytest.mark.asyncio
async def test_analyze_503_missing_provider():
    """Test that analyze endpoint returns 503 with proper details when provider missing."""
    from app.routes.orchestrator_minimal import AnalysisRequest
    from app.middleware.auth_middleware import AuthUser
    
    # Create mock app with orchestration service
    app_mock = Mock()
    app_mock.state.orchestration_service = OrchestrationService(
        model_registry=Mock(),
        rate_limiter=Mock()
    )
    
    # Mock to return only 2 providers (missing anthropic)
    app_mock.state.orchestration_service._default_models_from_env = AsyncMock(
        return_value=["gpt-4", "gemini-1.5-flash"]
    )
    
    # Create request mocks
    request_mock = Mock()
    request_mock.app = app_mock
    request_mock.state = Mock()
    request_mock.state.request_id = "test-123"
    request_mock.state.correlation_id = "test-123"
    
    analysis_request = AnalysisRequest(
        query="Test query",
        analysis_type="simple"
    )
    
    auth_user = AuthUser(user_id="test-user", username="test")
    
    # Get router and call analyze endpoint
    router = create_router()
    analyze_func = None
    for route in router.routes:
        if route.path == "/orchestrator/analyze" and route.methods == {"POST"}:
            analyze_func = route.endpoint
            break
    
    # Should raise HTTPException with 503
    with pytest.raises(HTTPException) as exc_info:
        await analyze_func(analysis_request, request_mock, auth_user)
    
    # Verify 503 error details
    assert exc_info.value.status_code == 503
    assert exc_info.value.detail["error"] == "SERVICE_UNAVAILABLE"
    # Depending on REQUIRED_PROVIDERS, message may prioritize providers or count
    assert (
        "Missing required providers" in exc_info.value.detail["message"]
        or "Insufficient healthy models" in exc_info.value.detail["message"]
    )
    assert "providers_present" in exc_info.value.detail["details"]
    assert "required_providers" in exc_info.value.detail["details"]
    # missing_providers is only populated when REQUIRED_PROVIDERS is set
    if exc_info.value.detail["details"].get("required_providers"):
        assert "missing_providers" in exc_info.value.detail["details"]


@pytest.mark.asyncio 
async def test_analyze_503_insufficient_models():
    """Test that analyze endpoint returns 503 with proper details when insufficient models."""
    from app.routes.orchestrator_minimal import AnalysisRequest
    from app.middleware.auth_middleware import AuthUser
    
    # Create mock app with orchestration service
    app_mock = Mock()
    app_mock.state.orchestration_service = OrchestrationService(
        model_registry=Mock(),
        rate_limiter=Mock()
    )
    
    # Mock to return only 1 model
    app_mock.state.orchestration_service._default_models_from_env = AsyncMock(
        return_value=["gpt-4"]
    )
    
    # Create request mocks
    request_mock = Mock()
    request_mock.app = app_mock
    request_mock.state = Mock()
    request_mock.state.request_id = "test-123"
    request_mock.state.correlation_id = "test-123"
    
    analysis_request = AnalysisRequest(
        query="Test query",
        analysis_type="simple"
    )
    
    auth_user = AuthUser(user_id="test-user", username="test")
    
    # Get router and call analyze endpoint
    router = create_router()
    analyze_func = None
    for route in router.routes:
        if route.path == "/orchestrator/analyze" and route.methods == {"POST"}:
            analyze_func = route.endpoint
            break
    
    # Should raise HTTPException with 503
    with pytest.raises(HTTPException) as exc_info:
        await analyze_func(analysis_request, request_mock, auth_user)
    
    # Verify 503 error details
    assert exc_info.value.status_code == 503
    assert exc_info.value.detail["error"] == "SERVICE_UNAVAILABLE"
    
    # When REQUIRED_PROVIDERS is set, provider error takes precedence
    import os
    if os.getenv("REQUIRED_PROVIDERS"):
        assert "Missing required providers" in exc_info.value.detail["message"]
        assert "missing_providers" in exc_info.value.detail["details"]
    else:
        assert "Insufficient healthy models" in exc_info.value.detail["message"]
        assert "required_models" in exc_info.value.detail["details"]
    
    assert "selected_models" in exc_info.value.detail["details"]
    assert "providers_present" in exc_info.value.detail["details"]
    assert "required_providers" in exc_info.value.detail["details"]


if __name__ == "__main__":
    asyncio.run(test_service_status_insufficient_models())
    asyncio.run(test_service_status_ready_with_big3())
    print("✅ All smoke tests passed!")
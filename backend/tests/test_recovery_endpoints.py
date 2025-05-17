"""Integration tests for recovery endpoints.

Tests the manual recovery API endpoints to ensure they work correctly
with proper authentication and error handling.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.routes.recovery_routes import get_recovery_workflow, recovery_workflow
from backend.utils.circuit_breaker import CircuitBreakerManager
from backend.utils.recovery_workflows import RecoveryConfig, RecoveryWorkflow


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Admin authentication headers for testing."""
    return {"Authorization": "Bearer admin_test_token"}


@pytest.fixture
def mock_recovery_workflow():
    """Mock recovery workflow for testing."""
    workflow = Mock(spec=RecoveryWorkflow)
    workflow.get_recovery_status = Mock(
        return_value={
            "active_recoveries": ["test_service"],
            "recent_recoveries": [
                {
                    "recovery_id": "TEST_ERROR:test_service",
                    "error_type": "TEST_ERROR",
                    "success": True,
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat(),
                }
            ],
            "recovery_stats": {
                "total_recoveries": 10,
                "success_rate": 0.8,
                "average_duration": 5.2,
            },
        }
    )
    workflow.handle_failure = AsyncMock(return_value=True)
    workflow.recovery_history = [
        {
            "recovery_id": "TEST_ERROR:test_service",
            "error_type": "TEST_ERROR",
            "success": True,
        }
    ]
    workflow._calculate_stats = Mock(
        return_value={"total_recoveries": 10, "success_rate": 0.8}
    )
    return workflow


@pytest.fixture
def mock_circuit_manager():
    """Mock circuit breaker manager for testing."""
    manager = Mock(spec=CircuitBreakerManager)
    manager.reset_breaker = AsyncMock(return_value=True)
    manager.get_all_statuses = Mock(
        return_value={
            "openai": {
                "name": "openai",
                "state": "open",
                "stats": {
                    "failure_count": 5,
                    "success_count": 10,
                    "total_requests": 15,
                },
            }
        }
    )
    return manager


class TestRecoveryStatusEndpoint:
    """Test recovery status endpoint."""

    def test_get_recovery_status_success(
        self, client, auth_headers, mock_recovery_workflow
    ):
        """Test successful retrieval of recovery status."""
        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow",
            return_value=mock_recovery_workflow,
        ):
            response = client.get("/api/recovery/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recovery_status" in data["data"]
        assert "active_recoveries" in data["data"]["recovery_status"]

    def test_get_recovery_status_unauthorized(self, client):
        """Test recovery status requires authentication."""
        response = client.get("/api/recovery/status")
        assert response.status_code == 401

    def test_get_recovery_status_non_admin(self, client):
        """Test recovery status requires admin role."""
        headers = {"Authorization": "Bearer user_token"}
        response = client.get("/api/recovery/status", headers=headers)
        assert response.status_code == 403


class TestTriggerRecoveryEndpoint:
    """Test manual recovery trigger endpoint."""

    def test_trigger_recovery_success(
        self, client, auth_headers, mock_recovery_workflow
    ):
        """Test successful recovery trigger."""
        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow",
            return_value=mock_recovery_workflow,
        ):
            response = client.post(
                "/api/recovery/trigger",
                headers=auth_headers,
                json={
                    "error_type": "TEST_ERROR",
                    "service_name": "test_service",
                    "context": {"test": "data"},
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["recovery_triggered"] is True

        # Verify workflow was called correctly
        mock_recovery_workflow.handle_failure.assert_called_once()
        args = mock_recovery_workflow.handle_failure.call_args
        assert args[0][0] == "TEST_ERROR"
        assert args[0][1]["service_name"] == "test_service"
        assert args[0][1]["manual_trigger"] is True

    def test_trigger_recovery_missing_error_type(
        self, client, auth_headers, mock_recovery_workflow
    ):
        """Test recovery trigger with missing error type."""
        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow",
            return_value=mock_recovery_workflow,
        ):
            response = client.post(
                "/api/recovery/trigger",
                headers=auth_headers,
                json={"service_name": "test_service"},
            )

        assert response.status_code == 400
        assert "error_type is required" in response.json()["detail"]

    def test_trigger_recovery_failure(
        self, client, auth_headers, mock_recovery_workflow
    ):
        """Test recovery trigger when recovery fails."""
        mock_recovery_workflow.handle_failure = AsyncMock(return_value=False)

        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow",
            return_value=mock_recovery_workflow,
        ):
            response = client.post(
                "/api/recovery/trigger",
                headers=auth_headers,
                json={"error_type": "TEST_ERROR", "service_name": "test_service"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Recovery failed"


class TestCircuitBreakerEndpoints:
    """Test circuit breaker management endpoints."""

    def test_reset_circuit_breaker_success(
        self, client, auth_headers, mock_circuit_manager
    ):
        """Test successful circuit breaker reset."""
        with patch(
            "backend.routes.recovery_routes.circuit_manager", mock_circuit_manager
        ):
            response = client.post(
                "/api/recovery/circuit-breaker/reset",
                headers=auth_headers,
                json={"service_name": "openai"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["service_name"] == "openai"
        assert data["data"]["action"] == "reset"

        mock_circuit_manager.reset_breaker.assert_called_once_with("openai")

    def test_reset_circuit_breaker_not_found(
        self, client, auth_headers, mock_circuit_manager
    ):
        """Test circuit breaker reset for non-existent service."""
        mock_circuit_manager.reset_breaker = AsyncMock(return_value=False)

        with patch(
            "backend.routes.recovery_routes.circuit_manager", mock_circuit_manager
        ):
            response = client.post(
                "/api/recovery/circuit-breaker/reset",
                headers=auth_headers,
                json={"service_name": "nonexistent"},
            )

        assert response.status_code == 404
        assert "Circuit breaker not found" in response.json()["detail"]

    def test_get_circuit_breaker_status(
        self, client, auth_headers, mock_circuit_manager
    ):
        """Test retrieval of circuit breaker status."""
        with patch(
            "backend.routes.recovery_routes.circuit_manager", mock_circuit_manager
        ):
            response = client.get(
                "/api/recovery/circuit-breaker/status", headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "circuit_breakers" in data["data"]
        assert "openai" in data["data"]["circuit_breakers"]


class TestCacheAndDatabaseEndpoints:
    """Test cache and database recovery endpoints."""

    def test_clear_cache_success(self, client, auth_headers, mock_recovery_workflow):
        """Test successful cache clearing."""
        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow",
            return_value=mock_recovery_workflow,
        ):
            response = client.post("/api/recovery/cache/clear", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["action"] == "cache_clear"

        # Verify recovery was triggered with correct parameters
        mock_recovery_workflow.handle_failure.assert_called_once()
        args = mock_recovery_workflow.handle_failure.call_args
        assert args[0][0] == "CACHE_CLEAR_REQUESTED"
        assert args[0][1]["clear_cache"] is True

    def test_reconnect_database_success(
        self, client, auth_headers, mock_recovery_workflow
    ):
        """Test successful database reconnection."""
        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow",
            return_value=mock_recovery_workflow,
        ):
            response = client.post(
                "/api/recovery/database/reconnect", headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["action"] == "database_reconnect"

        # Verify recovery was triggered
        mock_recovery_workflow.handle_failure.assert_called_once()
        args = mock_recovery_workflow.handle_failure.call_args
        assert args[0][0] == "DB_RECONNECT_REQUESTED"


class TestRecoveryHistoryEndpoints:
    """Test recovery history endpoints."""

    def test_get_recovery_history(self, client, auth_headers, mock_recovery_workflow):
        """Test retrieval of recovery history."""
        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow",
            return_value=mock_recovery_workflow,
        ):
            response = client.get(
                "/api/recovery/history", headers=auth_headers, params={"limit": 10}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "history" in data["data"]
        assert len(data["data"]["history"]) == 1

    def test_get_recovery_history_filtered(
        self, client, auth_headers, mock_recovery_workflow
    ):
        """Test filtered recovery history."""
        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow",
            return_value=mock_recovery_workflow,
        ):
            response = client.get(
                "/api/recovery/history",
                headers=auth_headers,
                params={"error_type": "TEST_ERROR"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert all(h["error_type"] == "TEST_ERROR" for h in data["data"]["history"])

    def test_get_recovery_stats(self, client, auth_headers, mock_recovery_workflow):
        """Test retrieval of recovery statistics."""
        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow",
            return_value=mock_recovery_workflow,
        ):
            response = client.get("/api/recovery/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "stats" in data["data"]
        assert data["data"]["stats"]["total_recoveries"] == 10
        assert data["data"]["stats"]["success_rate"] == 0.8


class TestRecoveryIntegration:
    """Test full recovery flow integration."""

    @pytest.mark.asyncio
    async def test_full_recovery_flow(self, client, auth_headers):
        """Test complete recovery flow from failure to recovery."""
        # This would be a more comprehensive integration test
        # that actually triggers failures and verifies recovery
        # For now, we'll mock the key components

        with patch(
            "backend.routes.recovery_routes.get_recovery_workflow"
        ) as mock_get_workflow:
            with patch(
                "backend.routes.recovery_routes.circuit_manager"
            ) as mock_circuit:
                # Setup mocks
                workflow = Mock()
                workflow.handle_failure = AsyncMock(return_value=True)
                workflow.get_recovery_status = Mock(
                    return_value={
                        "active_recoveries": [],
                        "recent_recoveries": [],
                        "recovery_stats": {},
                    }
                )

                mock_get_workflow.return_value = workflow
                mock_circuit.get_all_statuses.return_value = {}

                # 1. Check initial status
                response = client.get("/api/recovery/status", headers=auth_headers)
                assert response.status_code == 200

                # 2. Trigger a recovery
                response = client.post(
                    "/api/recovery/trigger",
                    headers=auth_headers,
                    json={"error_type": "SERVICE_DOWN", "service_name": "test_service"},
                )
                assert response.status_code == 200

                # 3. Check status again
                response = client.get("/api/recovery/status", headers=auth_headers)
                assert response.status_code == 200

                # Verify workflow was called
                workflow.handle_failure.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import pytest
from unittest.mock import patch, AsyncMock
import os

@pytest.mark.asyncio
async def test_big_3_gating_preserved_with_enhanced_synthesis(client):
    """
    Validates that the Big 3 gating is still enforced even when the
    enhanced synthesis feature flag is enabled. The service should return a 503
    if one of the required providers is unavailable.
    """
    # Enable the enhanced synthesis feature flag
    with patch('os.environ.get') as mock_env_get:
        # Let the flag return true, but have other os.environ.get calls work normally
        mock_env_get.side_effect = lambda key, default=None: "true" if key == "ENHANCED_SYNTHESIS_ENABLED" else os.environ.get(key, default)

        # Mock the health manager to report that a required provider is missing
        with patch('app.services.orchestration_service.provider_health_manager.get_health_summary', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = {
                "_system": {
                    "available_providers": ["openai", "anthropic"], # Google is missing
                    "total_providers": 2,
                    "meets_requirements": False
                }
            }
            
            # Make a request to the analyze endpoint
            response = client.post(
                "/api/orchestrator/analyze",
                json={"query": "test", "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022"]},
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Assertion: We expect a 503 Service Unavailable, not a 200 OK.
            # This confirms that the gating logic runs before the new synthesis logic.
            assert response.status_code == 503
            
            data = response.json()
            assert "error_details" in data
            assert "google" in data["error_details"]["required_providers"]
            assert "google" not in data["error_details"]["providers_present"]

@pytest.mark.asyncio
async def test_no_cost_fields_in_api_response(client):
    """
    Validates that no cost or billing-related fields are present in the
    final API response, adhering to the no-cost policy.
    """
    # Mock health to ensure the request goes through
    with patch('app.services.orchestration_service.provider_health_manager.get_health_summary', new_callable=AsyncMock) as mock_health:
        mock_health.return_value = {
            "_system": {"available_providers": ["openai", "anthropic", "google"], "meets_requirements": True}
        }

        # Mock the pipeline to return a predictable result
        with patch('app.services.orchestration_service.OrchestrationService.run_pipeline', new_callable=AsyncMock) as mock_run_pipeline:
            mock_run_pipeline.return_value = {
                "ultra_synthesis": {
                    "output": "synthesis result",
                    "cost": 0.05, # Intentionally add a forbidden field
                    "billing_code": "xyz-123" # Add another forbidden field
                },
                "_metadata": {}
            }

            response = client.post(
                "/api/orchestrator/analyze",
                json={"query": "test", "selected_models": ["gpt-4o"]},
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200, response.text
            
            data = response.json()
            
            # Recursively check the response data for forbidden keys
            def check_for_forbidden_keys(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        assert "cost" not in key.lower()
                        assert "billing" not in key.lower()
                        check_for_forbidden_keys(value)
                elif isinstance(obj, list):
                    for item in obj:
                        check_for_forbidden_keys(item)

            check_for_forbidden_keys(data)
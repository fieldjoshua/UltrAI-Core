import pytest
from unittest.mock import patch, AsyncMock, MagicMock

# The TestClient is now provided by the conftest.py fixture

@pytest.mark.asyncio
async def test_enhanced_synthesis_flag_enabled(client):
    """
    Smoke test to verify that when ENHANCED_SYNTHESIS_ENABLED is true,
    the enhanced synthesis prompt manager is used.
    """
    # Set the feature flag environment variable
    with patch('os.environ.get', return_value="true"):
        # We need to mock the dependencies of OrchestrationService
        with patch('app.services.orchestration_service.SynthesisPromptManager') as MockPromptManager, \
             patch('app.services.orchestration_service.provider_health_manager.get_health_summary', new_callable=AsyncMock) as mock_health:
            
            # Ensure the service is reported as healthy
            mock_health.return_value = {
                "_system": {"available_providers": ["openai", "anthropic", "google"], "meets_requirements": True}
            }

            # Mock the prompt manager instance to track its usage
            mock_prompt_manager_instance = MockPromptManager.return_value
            mock_prompt_manager_instance.get_synthesis_prompt = MagicMock(return_value="enhanced prompt")

            # Make a request to the analyze endpoint
            response = client.post(
                "/api/orchestrator/analyze",
                json={"query": "test", "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]},
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Assertions
            assert response.status_code == 200, response.text
            
            # Verify that the enhanced prompt manager was called.
            # This confirms the feature flag logic is working.
            mock_prompt_manager_instance.get_synthesis_prompt.assert_called()

@pytest.mark.asyncio
async def test_enhanced_synthesis_flag_disabled(client):
    """
    Smoke test to verify that when ENHANCED_SYNTHESIS_ENABLED is false,
    the enhanced synthesis prompt manager is NOT used.
    """
    # Set the feature flag environment variable to false
    with patch('os.environ.get', return_value="false"):
        with patch('app.services.orchestration_service.SynthesisPromptManager') as MockPromptManager, \
             patch('app.services.orchestration_service.provider_health_manager.get_health_summary', new_callable=AsyncMock) as mock_health:
            
            mock_health.return_value = {
                "_system": {"available_providers": ["openai", "anthropic", "google"], "meets_requirements": True}
            }

            mock_prompt_manager_instance = MockPromptManager.return_value
            mock_prompt_manager_instance.get_synthesis_prompt = MagicMock(return_value="enhanced prompt")

            response = client.post(
                "/api/orchestrator/analyze",
                json={"query": "test", "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]},
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200, response.text
            
            # Verify that the enhanced prompt manager was NOT called.
            mock_prompt_manager_instance.get_synthesis_prompt.assert_not_called()

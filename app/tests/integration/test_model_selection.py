import pytest
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_non_participant_model_selection(client):
    """
    Smoke test to verify that models used in initial responses are excluded
    from the final synthesis stage.
    """
    # Models used in the initial stage
    initial_models = ["gpt-4o", "gemini-1.5-pro"]
    
    # A different model that should be selected for synthesis
    synthesis_candidate = "claude-3-5-sonnet-20241022"

    # We need to mock the SmartModelSelector to check its inputs
    with patch('app.services.orchestration_service.SmartModelSelector') as MockModelSelector, \
         patch('app.services.orchestration_service.provider_health_manager.get_health_summary', new_callable=AsyncMock) as mock_health:

        # Ensure the service is healthy
        mock_health.return_value = {
            "_system": {"available_providers": ["openai", "anthropic", "google"], "meets_requirements": True}
        }

        # Mock the model selector instance to control its return value and track calls
        mock_selector_instance = MockModelSelector.return_value
        # Ensure the candidate list passed to the selector is what we expect
        mock_selector_instance.select_best_synthesis_model = AsyncMock(return_value=[synthesis_candidate])

        # Simulate a pipeline result from a previous stage
        # This would be the input to the ultra_synthesis stage
        # We need to patch the entire run_pipeline method to simulate this state
        with patch('app.services.orchestration_service.OrchestrationService._run_stage', new_callable=AsyncMock) as mock_run_stage:
            # Let the first two stages return successfully
            mock_run_stage.side_effect = [
                MagicMock(output={"responses": {"gpt-4o": "resp1", "gemini-1.5-pro": "resp2"}, "successful_models": initial_models}),
                MagicMock(output={"revised_responses": {"gpt-4o": "rev1", "gemini-1.5-pro": "rev2"}, "successful_models": initial_models}),
                # For the ultra_synthesis stage, just return a mock
                MagicMock(output={"synthesis": "final_synthesis"})
            ]

            client.post(
                "/api/orchestrator/analyze",
                json={"query": "test", "selected_models": initial_models},
                headers={"Authorization": "Bearer test-token"}
            )
            
            # The actual assertion is on the mock call
            # Find the call to select_best_synthesis_model and inspect available_models
            call_args, call_kwargs = mock_selector_instance.select_best_synthesis_model.call_args
            
            # The available_models list passed to the selector should NOT contain the initial models
            available_for_synthesis = call_kwargs.get("available_models", [])
            
            assert "gpt-4o" not in available_for_synthesis
            assert "gemini-1.5-pro" not in available_for_synthesis
            
            # It should contain our expected candidate
            assert synthesis_candidate in available_for_synthesis
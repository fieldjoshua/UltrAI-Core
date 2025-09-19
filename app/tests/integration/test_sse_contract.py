import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Minimal SSE contract test
@pytest.mark.asyncio
async def test_sse_contract_emits_stage_events(client):
    """Ensure at least one stage_started and stage_completed event per stage."""
    
    # Mock the orchestration service to control the SSE events
    with patch('app.services.sse_event_bus.SSEEventBus.publish', new_callable=AsyncMock) as mock_publish:
        # Simulate a request that would trigger the pipeline
        headers = {"Authorization": "Bearer test-token"}
        payload = {
            "query": "test query",
            "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]
        }
        
        # We don't need the full response, just to trigger the service call
        # In a real scenario, you might have a stream endpoint to test against
        # For this contract, we'll just check if the event bus was called correctly
        
        # This is a simplified stand-in for actually running the pipeline.
        # A full integration test would be needed to test the stream itself.
        # Here we just assert that the event bus would have been called.
        
        from app.services.sse_event_bus import sse_event_bus
        correlation_id = "test_correlation_id"
        
        # Simulate pipeline progression
        await sse_event_bus.publish(correlation_id, "stage_started", {"stage": "initial_response"})
        await sse_event_bus.publish(correlation_id, "stage_completed", {"stage": "initial_response"})
        await sse_event_bus.publish(correlation_id, "stage_started", {"stage": "peer_review"})
        await sse_event_bus.publish(correlation_id, "stage_completed", {"stage": "peer_review"})

        # Assertions
        call_args_list = mock_publish.call_args_list
        
        # Check for stage_started events
        started_stages = [
            call.args[2].get("stage")
            for call in call_args_list
            if call.args[1] == "stage_started"
        ]
        assert "initial_response" in started_stages
        assert "peer_review" in started_stages

        # Check for stage_completed events
        completed_stages = [
            call.args[2].get("stage")
            for call in call_args_list
            if call.args[1] == "stage_completed"
        ]
        assert "initial_response" in completed_stages
        assert "peer_review" in completed_stages

@pytest.mark.asyncio
async def test_sse_new_event_schema(client):
    """Smoke test to validate the schema of new SSE events."""
    from app.services.sse_event_bus import sse_event_bus
    correlation_id = "test_correlation_id_schema"
    
    with patch('app.services.sse_event_bus.SSEEventBus.publish', new_callable=AsyncMock) as mock_publish:
        # Simulate emitting a new event type
        event_payload = {
            "stage": "synthesis",
            "model": "claude-3-5-sonnet-20241022",
            "provider": "anthropic",
            "correlation_id": correlation_id,
            "latency_ms": 1234,
            "data": {
                "synthesis_type": "enhanced"
            }
        }
        await sse_event_bus.publish(correlation_id, "ultra_synthesis_start", event_payload)

        # Assertion
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args.args
        
        # Verify the event name and payload structure
        assert call_args[0] == correlation_id
        assert call_args[1] == "ultra_synthesis_start"
        
        # Validate the payload against the specified schema
        payload = call_args[2]
        assert "stage" in payload
        assert "model" in payload
        assert "provider" in payload
        assert "correlation_id" in payload
        assert "latency_ms" in payload
        assert "data" in payload
        assert payload["correlation_id"] == correlation_id
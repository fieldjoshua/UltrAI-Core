"""
Integration tests for SSE events functionality.
"""

import asyncio
import json
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.app import create_app
from app.services.sse_event_bus import sse_event_bus


@pytest.mark.integration
class TestSSEEvents:
    """Test SSE events integration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_sse_events_endpoint_basic_connection(self, client):
        """Test basic SSE connection and heartbeat."""
        correlation_id = "test_sse_123"

        # Connect to SSE stream
        with client.stream("GET", f"/api/orchestrator/events?correlation_id={correlation_id}") as stream:
            # Should receive initial connected event
            connected_data = next(stream)
            assert connected_data.startswith("event: connected")
            assert "data: " in connected_data

            # Should receive heartbeat within 20 seconds
            heartbeat_data = None
            for _ in range(40):  # Wait up to 20 seconds (40 * 0.5s)
                try:
                    heartbeat_data = next(stream)
                    if "heartbeat" in heartbeat_data:
                        break
                except StopIteration:
                    break
                await asyncio.sleep(0.5)

            assert heartbeat_data is not None
            assert "heartbeat" in heartbeat_data

    @pytest.mark.asyncio
    async def test_sse_events_named_events(self, client):
        """Test publishing and receiving named SSE events."""
        correlation_id = "test_sse_named_456"

        # Connect to SSE stream in background
        events_received = []

        async def consume_events():
            with client.stream("GET", f"/api/orchestrator/events?correlation_id={correlation_id}") as stream:
                for event_data in stream:
                    events_received.append(event_data)
                    if len(events_received) >= 5:  # Stop after a few events
                        break

        # Start consuming events
        consume_task = asyncio.create_task(consume_events())

        # Wait a moment for connection
        await asyncio.sleep(0.1)

        # Publish test events
        await sse_event_bus.publish(correlation_id, "analysis_start", {"models": ["gpt-4", "claude-3"]})
        await sse_event_bus.publish(correlation_id, "model_selected", {"model": "gpt-4"})
        await sse_event_bus.publish(correlation_id, "pipeline_complete", {"success": True})

        # Wait for events to be processed
        await asyncio.sleep(0.5)

        # Cancel consumption task
        consume_task.cancel()

        # Verify events were received
        event_lines = "\n".join(events_received)
        assert "event: connected" in event_lines
        assert "event: analysis_start" in event_lines
        assert "event: model_selected" in event_lines
        assert "event: pipeline_complete" in event_lines

        # Verify data payloads
        assert '"models": ["gpt-4", "claude-3"]' in event_lines
        assert '"model": "gpt-4"' in event_lines
        assert '"success": true' in event_lines

    @pytest.mark.asyncio
    async def test_sse_events_invalid_correlation_id(self, client):
        """Test SSE endpoint with invalid correlation ID."""
        # Should handle gracefully without crashing
        response = client.get("/api/orchestrator/events?correlation_id=invalid-id-with-spaces")
        # The endpoint should return a valid SSE stream even with potentially problematic IDs

    def test_sse_events_route_exists(self, client):
        """Test that the SSE events route is properly configured."""
        response = client.get("/api/orchestrator/events?correlation_id=test")
        assert response.status_code in [200, 503]  # 200 for success, 503 if service unavailable

    @pytest.mark.asyncio
    async def test_sse_events_concurrent_connections(self, client):
        """Test multiple concurrent SSE connections."""
        correlation_ids = ["concurrent_1", "concurrent_2", "concurrent_3"]

        async def connect_and_receive(corr_id):
            events = []
            with client.stream("GET", f"/api/orchestrator/events?correlation_id={corr_id}") as stream:
                for i, event_data in enumerate(stream):
                    events.append(event_data)
                    if i >= 2:  # Get a few events
                        break
            return events

        # Start multiple connections
        tasks = [connect_and_receive(corr_id) for corr_id in correlation_ids]
        results = await asyncio.gather(*tasks)

        # Each connection should have received events
        for events in results:
            assert len(events) > 0
            assert any("connected" in event for event in events)

    @pytest.mark.asyncio
    async def test_sse_events_service_unavailable_event(self, client):
        """Test service unavailable event handling."""
        correlation_id = "test_unavailable_789"

        # Connect to SSE stream
        events_received = []

        async def consume_events():
            with client.stream("GET", f"/api/orchestrator/events?correlation_id={correlation_id}") as stream:
                for event_data in stream:
                    events_received.append(event_data)
                    if len(events_received) >= 3:  # Stop after a few events
                        break

        # Start consuming events
        consume_task = asyncio.create_task(consume_events())

        # Wait for connection
        await asyncio.sleep(0.1)

        # Publish service unavailable event
        await sse_event_bus.publish(correlation_id, "service_unavailable", {
            "error": "All providers unavailable",
            "providers": ["openai", "anthropic"]
        })

        # Wait for event to be processed
        await asyncio.sleep(0.5)

        # Cancel consumption task
        consume_task.cancel()

        # Verify service unavailable event was received
        event_lines = "\n".join(events_received)
        assert "event: service_unavailable" in event_lines
        assert '"error": "All providers unavailable"' in event_lines
        assert '"providers": ["openai", "anthropic"]' in event_lines

    @pytest.mark.asyncio
    async def test_sse_events_json_parsing(self, client):
        """Test that SSE event data is properly JSON parseable."""
        correlation_id = "test_json_101112"

        # Connect to SSE stream
        events_received = []

        async def consume_events():
            with client.stream("GET", f"/api/orchestrator/events?correlation_id={correlation_id}") as stream:
                for event_data in stream:
                    events_received.append(event_data)
                    if len(events_received) >= 2:  # Get connected + one more event
                        break

        # Start consuming events
        consume_task = asyncio.create_task(consume_events())

        # Wait for connection
        await asyncio.sleep(0.1)

        # Publish event with complex JSON data
        test_data = {
            "stage": "ultra_synthesis",
            "models": ["gpt-4"],
            "metadata": {
                "processing_time": 12.5,
                "tokens_used": 1500
            }
        }
        await sse_event_bus.publish(correlation_id, "stage_completed", test_data)

        # Wait for event to be processed
        await asyncio.sleep(0.5)

        # Cancel consumption task
        consume_task.cancel()

        # Find the stage_completed event
        stage_event = None
        for event in events_received:
            if "event: stage_completed" in event:
                stage_event = event
                break

        assert stage_event is not None

        # Extract and parse JSON data
        lines = stage_event.split('\n')
        data_line = None
        for line in lines:
            if line.startswith('data: '):
                data_line = line[6:]  # Remove 'data: ' prefix
                break

        assert data_line is not None
        parsed_data = json.loads(data_line)

        # Verify structure matches expected format
        assert parsed_data["event"] == "stage_completed"
        assert "data" in parsed_data
        assert parsed_data["data"]["stage"] == "ultra_synthesis"
        assert parsed_data["data"]["models"] == ["gpt-4"]
        assert "metadata" in parsed_data["data"]
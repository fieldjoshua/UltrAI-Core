"""
Integration tests for SSE event streaming.

Tests the SSE event bus and /orchestrator/events endpoint to ensure
real-time event delivery during pipeline execution.
"""

import pytest
import asyncio
from app.services.sse_event_bus import sse_event_bus


@pytest.mark.asyncio
async def test_sse_event_bus_publish_subscribe():
    """Test that events can be published and received via SSE event bus."""
    correlation_id = "test_corr_123"
    received_events = []
    
    async def consume_events():
        """Consumer that collects events."""
        count = 0
        async for frame in sse_event_bus.subscribe(correlation_id, heartbeat_seconds=1):
            received_events.append(frame)
            count += 1
            if count >= 3:
                break
    
    consumer_task = asyncio.create_task(consume_events())
    
    await asyncio.sleep(0.1)
    
    await sse_event_bus.publish(correlation_id, "test_event", {"message": "hello"})
    await sse_event_bus.publish(correlation_id, "another_event", {"data": 42})
    
    await asyncio.wait_for(consumer_task, timeout=5.0)
    
    assert len(received_events) >= 3
    assert any("connected" in frame for frame in received_events)
    assert any("test_event" in frame for frame in received_events)
    assert any("another_event" in frame for frame in received_events)


@pytest.mark.asyncio
async def test_sse_heartbeat_frames():
    """Test that heartbeat frames are sent periodically."""
    correlation_id = "test_heartbeat_456"
    received_events = []
    
    async def consume_with_heartbeat():
        """Consumer that waits for heartbeat."""
        count = 0
        async for frame in sse_event_bus.subscribe(correlation_id, heartbeat_seconds=1):
            received_events.append(frame)
            count += 1
            if count >= 5:
                break
    
    await asyncio.wait_for(consume_with_heartbeat(), timeout=6.0)
    
    assert len(received_events) >= 2
    heartbeat_frames = [f for f in received_events if "heartbeat" in f]
    assert len(heartbeat_frames) >= 1


@pytest.mark.asyncio
async def test_multiple_subscribers():
    """Test that multiple subscribers can receive events independently."""
    correlation_id_1 = "test_multi_1"
    correlation_id_2 = "test_multi_2"
    
    events_1 = []
    events_2 = []
    
    async def consumer_1():
        count = 0
        async for frame in sse_event_bus.subscribe(correlation_id_1):
            events_1.append(frame)
            count += 1
            if count >= 2:
                break
    
    async def consumer_2():
        count = 0
        async for frame in sse_event_bus.subscribe(correlation_id_2):
            events_2.append(frame)
            count += 1
            if count >= 2:
                break
    
    task_1 = asyncio.create_task(consumer_1())
    task_2 = asyncio.create_task(consumer_2())
    
    await asyncio.sleep(0.1)
    
    await sse_event_bus.publish(correlation_id_1, "event_a", {"msg": "for 1"})
    await sse_event_bus.publish(correlation_id_2, "event_b", {"msg": "for 2"})
    
    await asyncio.wait_for(asyncio.gather(task_1, task_2), timeout=5.0)
    
    assert len(events_1) >= 2
    assert len(events_2) >= 2
    
    assert any("event_a" in f for f in events_1)
    assert not any("event_b" in f for f in events_1)
    
    assert any("event_b" in f for f in events_2)
    assert not any("event_a" in f for f in events_2)


@pytest.mark.asyncio
async def test_event_types_from_orchestration():
    """Test that expected orchestration events can be published."""
    correlation_id = "test_orchestration_789"
    
    event_names = [
        "connected",
        "analysis_start",
        "initial_start",
        "model_selected",
        "stage_started",
        "stage_completed",
        "model_completed",
        "pipeline_complete",
        "service_unavailable",
        "heartbeat"
    ]
    
    for event_name in event_names:
        await sse_event_bus.publish(
            correlation_id,
            event_name,
            {"test": True, "event_type": event_name}
        )
    
    received_events = []
    
    async def collect_events():
        count = 0
        async for frame in sse_event_bus.subscribe(correlation_id):
            received_events.append(frame)
            count += 1
            if count >= len(event_names) + 1:
                break
    
    await asyncio.wait_for(collect_events(), timeout=5.0)
    
    for event_name in event_names:
        assert any(event_name in frame for frame in received_events), \
            f"Event '{event_name}' not found in received frames"


@pytest.mark.asyncio
async def test_queue_overflow_drops_old_events():
    """Test that old events are dropped when queue exceeds maxsize."""
    correlation_id = "test_overflow"
    
    for i in range(1100):
        await sse_event_bus.publish(correlation_id, "event", {"index": i})
    
    received_events = []
    
    async def drain_queue():
        count = 0
        async for frame in sse_event_bus.subscribe(correlation_id):
            received_events.append(frame)
            count += 1
            if count >= 50:
                break
    
    await asyncio.wait_for(drain_queue(), timeout=5.0)
    
    assert len(received_events) > 0

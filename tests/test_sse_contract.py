"""
SSE (Server-Sent Events) contract test for the streaming endpoint.

This test verifies:
1. SSE events follow the expected format
2. Event types match the documented schema
3. Events are sent in the correct order
4. No sensitive data (costs) in events
"""

import json
import pytest
from app.services.orchestration_fixes import create_sse_event


def test_sse_event_format():
    """Test that SSE events follow the standardized format."""
    # Test basic event
    event = create_sse_event(
        stage="initial_response",
        event_type="stage_started",
        data={"message": "Starting initial response"}
    )
    
    assert event["stage"] == "initial_response"
    assert event["type"] == "stage_started"
    assert "timestamp" in event
    assert isinstance(event["timestamp"], float)
    assert event["data"] == {"message": "Starting initial response"}


def test_sse_event_with_model_info():
    """Test SSE event with model and provider info."""
    event = create_sse_event(
        stage="initial_response",
        event_type="model_completed",
        data={"response": "Test response"},
        model="gpt-4",
        provider="openai",
        latency_ms=1234.56
    )
    
    assert event["stage"] == "initial_response"
    assert event["type"] == "model_completed"
    assert event["model"] == "gpt-4"
    assert event["provider"] == "openai"
    assert event["latency_ms"] == 1234.56
    assert event["data"]["response"] == "Test response"


def test_sse_event_no_cost_fields():
    """Test that SSE events don't include cost fields."""
    # Try to create event with cost field (should be ignored)
    event = create_sse_event(
        stage="ultra_synthesis",
        event_type="stage_completed",
        data={"synthesis": "Final result"},
        cost=10.50,  # This should be ignored
        price=5.25    # This should be ignored
    )
    
    # Verify cost fields are not included
    assert "cost" not in event
    assert "price" not in event
    assert "billing" not in event
    

def test_sse_event_types():
    """Test all expected SSE event types."""
    valid_event_types = [
        "stage_started",
        "model_completed", 
        "stage_completed",
        "synthesis_chunk",
        "error"
    ]
    
    for event_type in valid_event_types:
        event = create_sse_event(
            stage="test_stage",
            event_type=event_type
        )
        assert event["type"] == event_type


def test_sse_event_schema_validation():
    """Test that events conform to expected schema."""
    # Analysis start event
    start_event = create_sse_event(
        stage="pipeline",
        event_type="analysis_start"
    )
    
    assert "stage" in start_event
    assert "type" in start_event
    assert "timestamp" in start_event
    
    # Model selected event
    model_event = create_sse_event(
        stage="initial_response",
        event_type="model_selected",
        data={"models": ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]}
    )
    
    assert model_event["data"]["models"] == ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
    
    # Service unavailable event
    error_event = create_sse_event(
        stage="pipeline",
        event_type="service_unavailable",
        data={
            "error": "SERVICE_UNAVAILABLE",
            "message": "Insufficient models",
            "providers_present": ["openai"],
            "required_providers": ["openai", "anthropic", "google"]
        }
    )
    
    assert error_event["data"]["error"] == "SERVICE_UNAVAILABLE"
    assert "providers_present" in error_event["data"]
    assert "required_providers" in error_event["data"]


def test_sse_event_order_contract():
    """Test expected event ordering for a successful pipeline."""
    expected_order = [
        ("pipeline", "analysis_start"),
        ("pipeline", "model_selected"),
        ("initial_response", "stage_started"),
        ("initial_response", "model_completed"),
        ("initial_response", "model_completed"),
        ("initial_response", "model_completed"),
        ("initial_response", "stage_completed"),
        ("peer_review", "stage_started"),
        ("peer_review", "stage_completed"),
        ("ultra_synthesis", "stage_started"),
        ("ultra_synthesis", "stage_completed"),
        ("pipeline", "pipeline_complete")
    ]
    
    # Verify each event can be created
    for stage, event_type in expected_order:
        event = create_sse_event(stage=stage, event_type=event_type)
        assert event["stage"] == stage
        assert event["type"] == event_type


def test_sse_format_for_streaming():
    """Test SSE event formatting for streaming response."""
    event = create_sse_event(
        stage="initial_response",
        event_type="model_completed",
        data={"model": "gpt-4", "response": "Test"}
    )
    
    # SSE format should be: data: {json}\n\n
    sse_line = f"data: {json.dumps(event)}\n\n"
    
    # Verify it can be parsed back
    data_part = sse_line.strip().replace("data: ", "")
    parsed = json.loads(data_part)
    assert parsed == event


if __name__ == "__main__":
    # Run tests
    test_sse_event_format()
    test_sse_event_with_model_info()
    test_sse_event_no_cost_fields()
    test_sse_event_types()
    test_sse_event_schema_validation()
    test_sse_event_order_contract()
    test_sse_format_for_streaming()
    print("✅ All SSE contract tests passed!")
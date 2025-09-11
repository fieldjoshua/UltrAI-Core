"""
Unit tests for streaming orchestration functionality.

This module tests the streaming response capabilities of the orchestration
service, including Server-Sent Events formatting and real-time updates.
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from app.services.streaming_orchestration_service import StreamingOrchestrationService
from app.models.streaming_response import StreamEventType, StreamingConfig
from app.services.model_registry import ModelRegistry
from app.services.quality_evaluation import QualityEvaluationService
from app.services.rate_limiter import RateLimiter


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for streaming orchestration service."""
    return {
        "model_registry": Mock(spec=ModelRegistry),
        "quality_evaluator": Mock(spec=QualityEvaluationService),
        "rate_limiter": Mock(spec=RateLimiter)
    }


@pytest.fixture
def streaming_service(mock_dependencies):
    """Create a streaming orchestration service with mocked dependencies."""
    return StreamingOrchestrationService(**mock_dependencies)


class TestStreamingOrchestrationService:
    """Test streaming orchestration service functionality."""
    
    @pytest.mark.asyncio
    async def test_stream_pipeline_start_event(self, streaming_service):
        """Test that pipeline start event is emitted."""
        # Mock model validation
        streaming_service._validate_model_names = Mock(return_value=["gpt-4", "claude-3"])
        streaming_service._default_models_from_env = AsyncMock(return_value=["gpt-4", "claude-3"])
        
        # Collect first event
        events = []
        async for event in streaming_service.stream_pipeline(
            "Test query",
            selected_models=["gpt-4", "claude-3"]
        ):
            events.append(event)
            break  # Just get first event
        
        assert len(events) == 1
        
        # Parse SSE format
        event_data = events[0].strip().replace("data: ", "")
        parsed = json.loads(event_data)
        
        assert parsed["event"] == StreamEventType.PIPELINE_START.value
        assert parsed["sequence"] == 1
        assert "Test query" in parsed["data"]["query"]
        assert parsed["data"]["selected_models"] == ["gpt-4", "claude-3"]
    
    @pytest.mark.asyncio
    async def test_sse_format(self, streaming_service):
        """Test Server-Sent Event formatting."""
        event = streaming_service._create_event(
            StreamEventType.MODEL_START,
            {"model": "gpt-4", "stage": "initial_response"}
        )
        
        sse_output = streaming_service._format_sse(event)
        
        assert sse_output.startswith("data: ")
        assert sse_output.endswith("\n\n")
        
        # Parse the JSON data
        json_str = sse_output.replace("data: ", "").strip()
        parsed = json.loads(json_str)
        
        assert parsed["event"] == StreamEventType.MODEL_START.value
        assert parsed["data"]["model"] == "gpt-4"
        assert "timestamp" in parsed
        assert "sequence" in parsed
    
    @pytest.mark.asyncio
    async def test_stage_events_emitted(self, streaming_service):
        """Test that stage start/complete events are emitted."""
        # Mock dependencies
        streaming_service._validate_model_names = Mock(return_value=["gpt-4"])
        streaming_service._default_models_from_env = AsyncMock(return_value=["gpt-4"])
        
        # Mock stage execution
        with patch.object(streaming_service, "_stream_initial_response") as mock_initial:
            mock_initial.return_value = self._async_generator([])
            
            # Collect events
            events = []
            stage_events = []
            
            async for event in streaming_service.stream_pipeline(
                "Test query",
                selected_models=["gpt-4"]
            ):
                events.append(event)
                parsed = json.loads(event.replace("data: ", "").strip())
                
                if parsed["event"] in [StreamEventType.STAGE_START.value, StreamEventType.STAGE_COMPLETE.value]:
                    stage_events.append(parsed)
                
                # Stop after a few events to avoid full pipeline
                if len(events) > 5:
                    break
            
            # Should have stage start events
            stage_starts = [e for e in stage_events if e["event"] == StreamEventType.STAGE_START.value]
            assert len(stage_starts) > 0
            assert stage_starts[0]["data"]["stage_name"] == "initial_response"
    
    @pytest.mark.asyncio
    async def test_synthesis_chunking(self, streaming_service):
        """Test that synthesis text is properly chunked."""
        test_text = " ".join([f"Word{i}" for i in range(100)])  # 100 words
        
        chunks = streaming_service._chunk_text(test_text, chunk_size=10)
        
        assert len(chunks) == 10  # 100 words / 10 words per chunk
        assert all(len(chunk.split()) <= 10 for chunk in chunks)
        assert " ".join(chunks) == test_text  # Can reconstruct original
    
    @pytest.mark.asyncio
    async def test_model_response_streaming(self, streaming_service):
        """Test streaming of model responses."""
        # Mock model execution
        async def mock_execute(model, prompt):
            return {
                "generated_text": f"Response from {model}",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20}
            }
        
        streaming_service._execute_model_with_retry = mock_execute
        
        # Collect model response events
        model_events = []
        
        async for event in streaming_service._stream_initial_response(
            "Test prompt",
            ["gpt-4", "claude-3"]
        ):
            model_events.append(event)
        
        assert len(model_events) == 2  # One event per model
        
        # Check event structure
        for event in model_events:
            assert event.event in [StreamEventType.MODEL_RESPONSE.value, StreamEventType.MODEL_ERROR.value]
            if event.event == StreamEventType.MODEL_RESPONSE.value:
                assert "model" in event.data
                assert "response_text" in event.data
                assert event.data["response_text"].startswith("Response from")
    
    @pytest.mark.asyncio
    async def test_streaming_config(self, streaming_service):
        """Test streaming configuration options."""
        config = StreamingConfig(
            chunk_size=25,
            synthesis_streaming=True,
            include_partial_responses=False
        )
        
        assert config.chunk_size == 25
        assert config.synthesis_streaming is True
        assert config.include_partial_responses is False
    
    @pytest.mark.asyncio
    async def test_error_event_on_failure(self, streaming_service):
        """Test that error events are emitted on failures."""
        # Mock to raise an error during pipeline execution
        streaming_service._default_models_from_env = AsyncMock(return_value=[])
        streaming_service._validate_model_names = Mock(side_effect=ValueError("Invalid model"))
        
        events = []
        async for event in streaming_service.stream_pipeline("Test", selected_models=["bad-model"]):
            events.append(event)
        
        # Should have error events
        assert len(events) > 0
        
        # Parse SSE format events
        parsed_events = []
        for event in events:
            if event.startswith("data: ") and event.strip() != "data: ":
                try:
                    parsed_events.append(json.loads(event.replace("data: ", "").strip()))
                except json.JSONDecodeError:
                    pass
        
        error_events = [e for e in parsed_events if e.get("event") == StreamEventType.PIPELINE_ERROR.value]
        assert len(error_events) > 0
        assert "Invalid model" in str(error_events[0]["data"])
    
    async def _async_generator(self, items):
        """Helper to create async generator from list."""
        for item in items:
            yield item


class TestStreamingEndpoint:
    """Test the streaming endpoint integration."""
    
    @pytest.mark.asyncio
    async def test_streaming_endpoint_headers(self):
        """Test that streaming endpoint returns correct headers."""
        import os
        os.environ["TESTING"] = "true"
        os.environ["JWT_SECRET_KEY"] = "test-secret-key"
        os.environ["ENABLE_AUTH"] = "false"
        
        from fastapi.testclient import TestClient
        from app.app import create_app
        from app.config import Config
        Config.ENABLE_AUTH = False
        
        app = create_app()
        client = TestClient(app)
        
        # Mock the orchestration service to return quickly
        with patch.object(
            app.state.orchestration_service, 
            'stream_pipeline',
            return_value=self._async_generator(["data: test\n\n"])
        ):
            response = client.post(
                "/api/orchestrator/analyze/stream",
                json={
                    "query": "Test streaming",
                    "selected_models": ["gpt-4"],
                    "stream_stages": ["synthesis_chunks"]
                },
                stream=True
            )
            
            # Check SSE headers
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            assert response.headers.get("cache-control") == "no-cache"
            assert response.headers.get("x-accel-buffering") == "no"
    
    async def _async_generator(self, items):
        """Helper to create async generator from list."""
        for item in items:
            yield item
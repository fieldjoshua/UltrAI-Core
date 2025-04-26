import pytest
import asyncio
import logging
from datetime import datetime
from src.orchestrator import TriLLMOrchestrator
from src.models import ModelResponse, QualityMetrics


class MockMonitoringLLMClient:
    def __init__(self, name):
        self.name = name
        self.calls = 0

    async def generate(self, prompt):
        self.calls += 1
        return f"Response from {self.name} for: {prompt}"


@pytest.fixture
def monitoring_orchestrator():
    return TriLLMOrchestrator(
        llama_client=MockMonitoringLLMClient("Llama"),
        chatgpt_client=MockMonitoringLLMClient("ChatGPT"),
        gemini_client=MockMonitoringLLMClient("Gemini"),
        cache_enabled=True,
    )


@pytest.mark.asyncio
async def test_logging_setup(monitoring_orchestrator):
    # Verify logger is configured
    assert monitoring_orchestrator.logger is not None
    assert isinstance(monitoring_orchestrator.logger, logging.Logger)

    # Verify log level
    assert monitoring_orchestrator.logger.level == logging.INFO


@pytest.mark.asyncio
async def test_metrics_collection(monitoring_orchestrator):
    prompt = "Test metrics collection"
    result = await monitoring_orchestrator.process_responses(prompt)

    metrics = result["metrics"]

    # Verify all metrics are collected
    assert "response_times" in metrics
    assert "success_rates" in metrics
    assert "token_usage" in metrics
    assert "quality_scores" in metrics

    # Verify metrics are properly formatted
    assert isinstance(metrics["response_times"], list)
    assert isinstance(metrics["success_rates"], dict)
    assert isinstance(metrics["token_usage"], dict)
    assert isinstance(metrics["quality_scores"], dict)


@pytest.mark.asyncio
async def test_error_logging(monitoring_orchestrator):
    # Test error logging
    with pytest.raises(ValueError):
        await monitoring_orchestrator.process_responses("")

    # Verify error was logged
    log_records = monitoring_orchestrator.logger.handlers[0].buffer
    assert any("error" in record.lower() for record in log_records)


@pytest.mark.asyncio
async def test_performance_monitoring(monitoring_orchestrator):
    prompt = "Test performance monitoring"

    # Record start time
    start_time = datetime.now()

    # Process request
    result = await monitoring_orchestrator.process_responses(prompt)

    # Record end time
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Verify performance metrics
    metrics = result["metrics"]
    assert len(metrics["response_times"]) > 0
    assert all(isinstance(t, float) for t in metrics["response_times"])
    assert all(t >= 0 for t in metrics["response_times"])
    assert sum(metrics["response_times"]) <= duration


@pytest.mark.asyncio
async def test_health_check(monitoring_orchestrator):
    # Test health check
    health_status = await monitoring_orchestrator.check_health()

    assert health_status["status"] == "healthy"
    assert "timestamp" in health_status
    assert "components" in health_status

    # Verify component status
    components = health_status["components"]
    assert "llama" in components
    assert "chatgpt" in components
    assert "gemini" in components
    assert all(components[model]["status"] == "healthy" for model in components)


@pytest.mark.asyncio
async def test_alert_system(monitoring_orchestrator):
    # Test alert system
    alerts = await monitoring_orchestrator.check_alerts()

    assert isinstance(alerts, list)
    for alert in alerts:
        assert "level" in alert
        assert "message" in alert
        assert "timestamp" in alert
        assert alert["level"] in ["info", "warning", "error", "critical"]


@pytest.mark.asyncio
async def test_metrics_aggregation(monitoring_orchestrator):
    # Test metrics aggregation
    prompts = [f"Test aggregation {i}" for i in range(5)]

    for prompt in prompts:
        await monitoring_orchestrator.process_responses(prompt)

    aggregated_metrics = await monitoring_orchestrator.get_aggregated_metrics()

    assert "total_requests" in aggregated_metrics
    assert "average_response_time" in aggregated_metrics
    assert "success_rate" in aggregated_metrics
    assert "error_rate" in aggregated_metrics

    # Verify aggregated values
    assert aggregated_metrics["total_requests"] >= len(prompts)
    assert 0 <= aggregated_metrics["success_rate"] <= 1
    assert 0 <= aggregated_metrics["error_rate"] <= 1
    assert aggregated_metrics["average_response_time"] >= 0

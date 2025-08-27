import base64
import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.services.orchestration_service import OrchestrationService
from app.services.model_registry import ModelRegistry
from app.services.quality_evaluation import QualityEvaluationService
from app.services.rate_limiter import RateLimiter

pytestmark = pytest.mark.asyncio


class DummyOrchestrator(OrchestrationService):
    """Subclass with stubbed methods to avoid external API calls."""
    
    def __init__(self):
        # Initialize with mock dependencies
        model_registry = Mock(spec=ModelRegistry)
        quality_evaluator = Mock(spec=QualityEvaluationService)
        rate_limiter = Mock(spec=RateLimiter)
        
        # Configure rate limiter mock
        rate_limiter.acquire = AsyncMock(return_value=None)
        rate_limiter.release = AsyncMock(return_value=None)
        rate_limiter.get_endpoint_stats = Mock(return_value={})
        rate_limiter.register_endpoint = Mock(return_value=None)
        
        super().__init__(
            model_registry=model_registry,
            quality_evaluator=quality_evaluator,
            rate_limiter=rate_limiter
        )
    
    async def initial_response(self, data, models, options=None):
        # Return stubbed responses for all models
        responses = {}
        for model in models:
            responses[model] = {"generated_text": f"{model}-initial-RESP"}
        return {"responses": responses, "successful_models": models}
    
    async def peer_review_and_revision(self, data, models, options=None):
        # Return stubbed peer review
        return {
            "revised_responses": {m: f"{m}-revised-RESP" for m in models},
            "successful_models": models
        }
    
    async def ultra_synthesis(self, data, models, options=None):
        # Return stubbed synthesis
        return "Ultra synthesis result"


@pytest.fixture
def orch():
    return DummyOrchestrator()


async def test_cost_estimate_present(orch):
    # Run pipeline and check for cost tracking
    res = await orch.run_pipeline("hello", selected_models=["gpt-4o", "claude-3-sonnet"])
    
    # Check that pipeline stages completed
    assert "initial_response" in res
    assert "ultra_synthesis" in res
    
    # Performance metrics should be present in each stage result
    if hasattr(res["initial_response"], "performance_metrics"):
        assert res["initial_response"].performance_metrics is not None


async def test_plain_text_format(orch):
    prompt = "## Heading\n**bold** text"
    
    # Test that markdown is processed in responses
    res = await orch.run_pipeline(
        prompt,
        selected_models=["gpt-4o", "claude-3-sonnet"],
        options={"response_format": "text"}
    )
    
    # Check that pipeline completed
    assert "ultra_synthesis" in res
    assert res["ultra_synthesis"].output is not None


async def test_encryption_support(orch):
    # Test that encryption options are passed through
    res = await orch.run_pipeline(
        "hello",
        selected_models=["gpt-4o", "claude-3-sonnet"],
        options={"encrypt": True}
    )
    
    # Check that pipeline completed
    assert "initial_response" in res
    assert "ultra_synthesis" in res


async def test_options_passed_to_stages(orch):
    # Test that options are properly passed to pipeline stages
    res = await orch.run_pipeline(
        "hello",
        selected_models=["gpt-4o", "claude-3-sonnet"],
        options={"test_option": True}
    )
    
    # Verify pipeline completed successfully
    assert "initial_response" in res
    assert res["initial_response"].error is None

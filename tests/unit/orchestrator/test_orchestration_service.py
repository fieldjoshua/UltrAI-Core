import pytest
from app.services.orchestration_service import *  # noqa: F401,F403
from unittest.mock import Mock
from app.services.orchestration_service import OrchestrationService, PipelineResult
from app.services.rate_limiter import RateLimiter
from app.services.token_management_service import TokenManagementService
from app.services.transaction_service import TransactionService
from app.services.quality_evaluation import QualityEvaluationService


# Stub dependencies subclassing actual service types for typing compatibility
class DummyRateLimiter(RateLimiter):
    async def acquire(self, model):
        pass

    async def release(self, model, success=True):
        pass

    def get_endpoint_stats(self, model):
        return {}


class DummyTokenManager(TokenManagementService):
    async def track_usage(self, model, input_tokens, output_tokens, user_id):
        return Mock(total_cost=0)


class DummyTransactionService(TransactionService):
    async def deduct_cost(self, user_id, amount, description):
        return None


class DummyQualityEvaluator(QualityEvaluationService):
    async def evaluate_response(self, response, context=None):
        return None


# TODO: Implement unit tests for orchestration_service


@pytest.mark.asyncio
async def test_run_pipeline_completes_all_stages():
    # Instantiate service with stubbed dependencies
    service = OrchestrationService(
        model_registry=Mock(),
        quality_evaluator=DummyQualityEvaluator(),
        rate_limiter=DummyRateLimiter(),
        token_manager=DummyTokenManager(),
        transaction_service=DummyTransactionService(),
    )
    input_data = "test_input"
    results = await service.run_pipeline(input_data)
    expected_stages = [stage.name for stage in service.pipeline_stages]
    assert list(results.keys()) == expected_stages
    # Verify each stage output contains correct stage name and nested input
    prev_input = input_data
    for stage_name, result in results.items():
        assert isinstance(result, PipelineResult)
        # Stage output should include its name
        assert result.output["stage"] == stage_name
        # Stage input should be the output of the previous stage
        assert result.output["input"] == prev_input
        # Update prev_input for next iteration
        prev_input = result.output


@pytest.mark.asyncio
async def test_run_pipeline_stops_on_stage_error(monkeypatch):
    # Instantiate service with stubbed dependencies
    service = OrchestrationService(
        model_registry=Mock(),
        quality_evaluator=DummyQualityEvaluator(),
        rate_limiter=DummyRateLimiter(),
        token_manager=DummyTokenManager(),
        transaction_service=DummyTransactionService(),
    )

    # Cause the peer_review_and_revision stage to error
    async def fail_peer_review(data, models, options=None):
        raise ValueError("peer review fail")

    monkeypatch.setattr(service, "peer_review_and_revision", fail_peer_review)

    results = await service.run_pipeline("input")
    # Initial stage should succeed, peer review stage should error, then stop
    assert list(results.keys())[:2] == ["initial_response", "peer_review_and_revision"]
    peer_review_res = results["peer_review_and_revision"]
    assert peer_review_res.error is not None
    assert "peer review fail" in peer_review_res.error
    # Should not run further stages
    assert "ultra_synthesis" not in results
    assert "hyper_level_analysis" not in results

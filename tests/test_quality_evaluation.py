import pytest
from app.services.quality_evaluation import (
    QualityEvaluationService,
    QualityDimension,
    ResponseQuality,
)


@pytest.mark.asyncio
async def test_evaluate_response_defaults():
    service = QualityEvaluationService()
    quality = await service.evaluate_response("Test response")
    assert isinstance(quality, ResponseQuality)
    # Overall score placeholder
    assert quality.overall_score == 7.25
    # Check dimensions for all enum members
    dims = quality.dimensions
    assert isinstance(dims, dict)
    assert set(dims.keys()) == set(QualityDimension)
    # Scores are within expected range
    for dim_score in dims.values():
        assert 0 <= dim_score.score <= 10
    # Check lists are non-empty
    assert quality.strengths
    assert quality.weaknesses
    assert quality.recommendations


@pytest.mark.asyncio
async def test_compare_responses_returns_correct_keys():
    service = QualityEvaluationService()
    responses = ["A", "B"]
    evals = await service.compare_responses(responses)
    # Should have keys response_0 and response_1
    assert isinstance(evals, dict)
    assert list(evals.keys()) == ["response_0", "response_1"]
    for q in evals.values():
        assert isinstance(q, ResponseQuality)
        assert q.overall_score == 7.25


@pytest.mark.asyncio
async def test_generate_quality_report_selects_best():
    service = QualityEvaluationService()
    responses = ["first", "second"]
    evals = await service.compare_responses(responses)
    report = await service.generate_quality_report(evals)
    assert "summary" in report and report["summary"].startswith(
        "Quality comparison report"
    )
    assert report["comparisons"] == evals
    # Both have equal scores, so first should be selected
    assert report["best_response"] == "response_0"

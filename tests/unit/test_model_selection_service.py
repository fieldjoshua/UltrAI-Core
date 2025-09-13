import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_model_selection_ranks_models_by_score(tmp_path):
    from app.services.model_selection import SmartModelSelector

    metrics_file = tmp_path / "metrics.json"
    selector = SmartModelSelector(metrics_file=str(metrics_file))

    # Seed some performance so ordering is deterministic
    selector.update_model_performance("gpt-4", success=True, quality_score=9.0, response_time=3.0)
    selector.update_model_performance("claude-3-5-sonnet-20241022", success=True, quality_score=8.5, response_time=4.0)
    selector.update_model_performance("gemini-1.5-flash", success=False, quality_score=5.0, response_time=7.0)

    ranked = await selector.select_best_synthesis_model(
        [
            "gemini-1.5-flash",
            "gpt-4",
            "claude-3-5-sonnet-20241022",
        ],
        query_type="technical",
    )

    # Expect the higher quality/success to rank above the failing one
    assert ranked[0] in {"gpt-4", "claude-3-5-sonnet-20241022"}
    assert ranked[-1] == "gemini-1.5-flash"

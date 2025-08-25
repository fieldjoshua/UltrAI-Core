import asyncio
from typing import Dict

from app.services.model_selection_service import SmartModelSelectionService
from app.services.model_availability import ModelAvailability, AvailabilityStatus


def test_smart_model_selection_scoring_prefers_available_low_cost_and_low_latency():
    service = SmartModelSelectionService()

    # Mock availability results
    async def mock_check_all_models(models, query, parallel=True) -> Dict[str, ModelAvailability]:
        return {
            "cheap_fast": ModelAvailability(
                model_name="cheap_fast",
                status=AvailabilityStatus.AVAILABLE,
                response_time=0.2,
            ),
            "expensive_slow": ModelAvailability(
                model_name="expensive_slow",
                status=AvailabilityStatus.AVAILABLE,
                response_time=1.5,
            ),
            "unavailable": ModelAvailability(
                model_name="unavailable",
                status=AvailabilityStatus.ERROR,
                response_time=None,
            ),
        }

    service.availability_checker.check_all_models = mock_check_all_models  # type: ignore

    # Mock historical selector ordering (history slightly favors expensive_slow)
    async def mock_select_best_synthesis_model(available_models, query_type=None, recent_performers=None):
        return ["expensive_slow", "cheap_fast"]

    service.selector.select_best_synthesis_model = mock_select_best_synthesis_model  # type: ignore

    # Mock pricing (cheap_fast is cheaper)
    def mock_calculate_cost(model, token_count, tier="basic", features=None):
        if model == "cheap_fast":
            return {"cost": 0.01}
        if model == "expensive_slow":
            return {"cost": 0.2}
        return {"cost": 1.0}

    service.pricing.calculate_cost = mock_calculate_cost  # type: ignore

    selected = asyncio.get_event_loop().run_until_complete(
        service.choose_models(
            query="hello",
            candidate_models=["cheap_fast", "expensive_slow", "unavailable"],
            desired_count=2,
            query_type="technical",
        )
    )

    assert selected[0] == "cheap_fast"
    assert "unavailable" not in selected  # noqa: W391


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest  # noqa: E402
from app.services.token_management_service import (
    TokenManagementService,
    TokenCost,
)  # noqa: E402


@pytest.mark.asyncio
async def test_track_usage_unknown_model_raises():
    service = TokenManagementService()
    with pytest.raises(ValueError):
        await service.track_usage("unknown-model", 10, 20, "user1")


@pytest.mark.asyncio
async def test_track_usage_and_get_user_usage_and_total_cost():
    service = TokenManagementService()
    user_id = "test_user"
    assert service.get_total_cost(user_id) == 0.0

    cost = await service.track_usage("gpt-4", 100, 200, user_id)
    assert isinstance(cost, TokenCost)
    expected_cost = (100 / 1000) * 0.03 + (200 / 1000) * 0.06
    assert pytest.approx(cost.total_cost, rel=1e-3) == expected_cost

    usage_list = service.get_user_usage(user_id)
    assert len(usage_list) == 1
    assert usage_list[0] is cost

    assert pytest.approx(service.get_total_cost(user_id), rel=1e-3) == expected_cost


@pytest.mark.asyncio
async def test_update_cost_rates_affects_future_costs():
    service = TokenManagementService()
    user_id = "user2"
    new_rates = {"gpt-4": {"input": 0.05, "output": 0.1}}
    service.update_cost_rates(new_rates)

    cost = await service.track_usage("gpt-4", 1000, 0, user_id)
    expected_cost = (1000 / 1000) * 0.05
    assert pytest.approx(cost.total_cost, rel=1e-3) == expected_cost

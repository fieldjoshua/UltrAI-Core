"""
Unit tests for TokenManagementService.
"""

import pytest
from app.services.token_management_service import TokenManagementService, TokenCost


@pytest.fixture
def token_service():
    """Create a TokenManagementService instance for testing."""
    return TokenManagementService()


@pytest.mark.asyncio
async def test_track_usage(token_service):
    """Test tracking token usage and cost calculation."""
    # Test with GPT-4
    cost = await token_service.track_usage(
        model="gpt-4", input_tokens=1000, output_tokens=500, user_id="test_user"
    )

    assert isinstance(cost, TokenCost)
    assert cost.model == "gpt-4"
    assert cost.input_tokens == 1000
    assert cost.output_tokens == 500
    assert cost.input_cost_per_1k == 0.03
    assert cost.output_cost_per_1k == 0.06
    assert cost.total_cost == (1 * 0.03) + (0.5 * 0.06)  # $0.06 total


@pytest.mark.asyncio
async def test_get_user_usage(token_service):
    """Test retrieving user usage history."""
    # Add some usage records
    await token_service.track_usage(
        model="gpt-4", input_tokens=1000, output_tokens=500, user_id="test_user"
    )
    await token_service.track_usage(
        model="claude-3", input_tokens=2000, output_tokens=1000, user_id="test_user"
    )

    usage = token_service.get_user_usage("test_user")
    assert len(usage) == 2
    assert usage[0].model == "gpt-4"
    assert usage[1].model == "claude-3"


@pytest.mark.asyncio
async def test_get_total_cost(token_service):
    """Test calculating total cost for a user."""
    # Add usage records
    await token_service.track_usage(
        model="gpt-4", input_tokens=1000, output_tokens=500, user_id="test_user"
    )
    await token_service.track_usage(
        model="claude-3", input_tokens=2000, output_tokens=1000, user_id="test_user"
    )

    total_cost = token_service.get_total_cost("test_user")
    expected_cost = (1 * 0.03 + 0.5 * 0.06) + (2 * 0.015 + 1 * 0.075)
    assert total_cost == expected_cost


@pytest.mark.asyncio
async def test_update_cost_rates(token_service):
    """Test updating cost rates for models."""
    new_rates = {
        "gpt-4": {"input": 0.04, "output": 0.08},
        "new-model": {"input": 0.01, "output": 0.02},
    }

    token_service.update_cost_rates(new_rates)

    # Test with updated rates
    cost = await token_service.track_usage(
        model="gpt-4", input_tokens=1000, output_tokens=500, user_id="test_user"
    )
    assert cost.input_cost_per_1k == 0.04
    assert cost.output_cost_per_1k == 0.08
    assert cost.total_cost == (1 * 0.04) + (0.5 * 0.08)  # $0.08 total


@pytest.mark.asyncio
async def test_invalid_model(token_service):
    """Test handling of invalid model names."""
    with pytest.raises(ValueError, match="Unknown model"):
        await token_service.track_usage(
            model="invalid-model",
            input_tokens=1000,
            output_tokens=500,
            user_id="test_user",
        )

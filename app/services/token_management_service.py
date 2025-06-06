"""
Token Management Service

This service handles real-time cost tracking, usage monitoring, and pricing algorithms for LLM usage.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from app.utils.logging import get_logger

logger = get_logger("token_management_service")


@dataclass
class TokenCost:
    """Cost information for token usage."""

    model: str
    input_tokens: int
    output_tokens: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    timestamp: datetime = datetime.now()

    @property
    def total_cost(self) -> float:
        """Calculate total cost for the token usage."""
        input_cost = (self.input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (self.output_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost


class TokenManagementService:
    """Service for managing token usage and costs."""

    def __init__(self):
        """Initialize the token management service."""
        self._cost_rates = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "claude-3": {"input": 0.015, "output": 0.075},
            "gemini-pro": {"input": 0.0005, "output": 0.0005},
        }
        self._usage_history: Dict[str, list[TokenCost]] = {}

    async def track_usage(
        self, model: str, input_tokens: int, output_tokens: int, user_id: str
    ) -> TokenCost:
        """
        Track token usage and calculate costs.

        Args:
            model: The model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            user_id: ID of the user

        Returns:
            TokenCost: The cost information
        """
        if model not in self._cost_rates:
            raise ValueError(f"Unknown model: {model}")

        rates = self._cost_rates[model]
        cost = TokenCost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_per_1k=rates["input"],
            output_cost_per_1k=rates["output"],
        )

        if user_id not in self._usage_history:
            self._usage_history[user_id] = []
        self._usage_history[user_id].append(cost)

        logger.info(
            f"Tracked usage for {model}: {input_tokens} input, {output_tokens} output tokens. "
            f"Cost: ${cost.total_cost:.4f}"
        )

        return cost

    def get_user_usage(self, user_id: str) -> list[TokenCost]:
        """
        Get usage history for a user.

        Args:
            user_id: ID of the user

        Returns:
            list[TokenCost]: List of token costs
        """
        return self._usage_history.get(user_id, [])

    def get_total_cost(self, user_id: str) -> float:
        """
        Get total cost for a user.

        Args:
            user_id: ID of the user

        Returns:
            float: Total cost
        """
        return sum(cost.total_cost for cost in self.get_user_usage(user_id))

    def update_cost_rates(self, new_rates: Dict[str, Dict[str, float]]) -> None:
        """
        Update cost rates for models.

        Args:
            new_rates: New cost rates
        """
        self._cost_rates.update(new_rates)
        logger.info(f"Updated cost rates: {json.dumps(new_rates, indent=2)}")

"""
Smart model selection service combining availability, latency, cost, and historical performance.
"""

from typing import List, Optional, Dict

from app.services.model_selection import SmartModelSelector
from app.services.model_availability import ModelAvailabilityChecker, AvailabilityStatus
from app.services.pricing_calculator import PricingCalculator
from app.utils.logging import get_logger

logger = get_logger("model_selection_service")


class SmartModelSelectionService:
    """High-level service to pick best models given a query and candidates."""

    def __init__(self) -> None:
        self.selector = SmartModelSelector()
        self.pricing = PricingCalculator()
        self.availability_checker = ModelAvailabilityChecker(model_selector=self.selector)

        # Simple weights; can be tuned or made configurable
        self.weights = {
            "availability": 0.35,
            "latency": 0.25,
            "cost": 0.2,
            "history": 0.2,
        }

    async def choose_models(
        self,
        query: str,
        candidate_models: Optional[List[str]] = None,
        desired_count: int = 1,
        query_type: Optional[str] = None,
    ) -> List[str]:
        """
        Return ranked list of models.
        Falls back to default available models if candidates not provided.
        """
        try:
            models = candidate_models or list(self.selector.model_expertise.keys())

            # 1) Availability and latency
            availability_map = await self.availability_checker.check_all_models(
                models=models, query=query, parallel=True
            )

            # 2) Historical score (from SmartModelSelector)
            ranked_by_history = await self.selector.select_best_synthesis_model(
                available_models=models, query_type=query_type
            )
            history_rank = {m: (len(ranked_by_history) - i) for i, m in enumerate(ranked_by_history)}

            # 3) Cost (lower is better)
            cost_score: Dict[str, float] = {}
            for m in models:
                # Use 1000 tokens baseline
                cost_info = self.pricing.calculate_cost(m, 1000)
                cost = cost_info.get("cost", 0.0)
                # Invert and normalize (avoid div by zero)
                cost_score[m] = 1.0 / (1.0 + cost)

            # 4) Compose score
            composite: List[tuple[float, str]] = []
            for m in models:
                av = availability_map.get(m)
                if not av or av.status != AvailabilityStatus.AVAILABLE:
                    # Skip unavailable
                    continue
                # Normalize latency (lower is better)
                latency = av.response_time or 5.0
                latency_component = 1.0 / (1.0 + latency)

                availability_component = 1.0  # only available models here
                history_component = history_rank.get(m, 0) / max(len(models), 1)
                cost_component = cost_score.get(m, 0.0)

                score = (
                    self.weights["availability"] * availability_component
                    + self.weights["latency"] * latency_component
                    + self.weights["cost"] * cost_component
                    + self.weights["history"] * history_component
                )
                composite.append((score, m))

            composite.sort(reverse=True)
            return [m for _, m in composite[: max(1, desired_count)]]
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            # Fail-safe: return a reasonable default
            return ["gpt-4o"]  # noqa: W391

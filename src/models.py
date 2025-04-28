import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from src.core.cache_adapter import ResponseCacheAdapter


@dataclass
class QualityMetrics:
    """Track quality metrics for responses"""

    coherence_score: float = 0.0
    technical_depth: float = 0.0
    strategic_value: float = 0.0
    uniqueness: float = 0.0

    def average_score(self) -> float:
        return (
            sum(
                [
                    self.coherence_score,
                    self.technical_depth,
                    self.strategic_value,
                    self.uniqueness,
                ]
            )
            / 4
        )


@dataclass
class ModelResponse:
    """Enhanced response tracking"""

    model_name: str
    content: str
    stage: str
    timestamp: float
    tokens_used: int = 0
    quality: QualityMetrics = field(default_factory=QualityMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "model_name": self.model_name,
                "stage": self.stage,
                "timestamp": self.timestamp,
                "tokens_used": self.tokens_used,
                "quality_scores": {
                    "coherence": self.quality.coherence_score,
                    "technical_depth": self.quality.technical_depth,
                    "strategic_value": self.quality.strategic_value,
                    "uniqueness": self.quality.uniqueness,
                    "average": self.quality.average_score(),
                },
                "metadata": self.metadata,
            }
        )


class ResponseCache:
    """Cache system for model responses"""

    def __init__(self, max_age_hours: int = 24):
        self.logger = logging.getLogger(__name__)
        # Use the adapter to connect to UnifiedCache
        self.adapter = ResponseCacheAdapter(max_age_hours=max_age_hours)
        self.logger.info(f"ResponseCache initialized with TTL: {max_age_hours} hours")

    def get(self, key: str) -> Optional[ModelResponse]:
        """Get a cached response."""
        return self.adapter.get(key)

    def set(self, key: str, response: ModelResponse):
        """Cache a response."""
        self.adapter.set(key, response)

    def clear_expired(self):
        """Clear expired cache entries."""
        self.adapter.clear_expired()

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        return self.adapter.get_metrics()

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


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
        self.cache: Dict[str, Dict] = {}
        self.max_age_hours = max_age_hours

    def get(self, key: str) -> Optional[ModelResponse]:
        if key not in self.cache:
            return None

        entry = self.cache[key]
        age = datetime.now() - entry["timestamp"]

        if age.total_seconds() > (self.max_age_hours * 3600):
            del self.cache[key]
            return None

        return entry["response"]

    def set(self, key: str, response: ModelResponse):
        self.cache[key] = {"response": response, "timestamp": datetime.now()}

    def clear_expired(self):
        current_time = datetime.now()
        expired_keys = [
            key
            for key, entry in self.cache.items()
            if (current_time - entry["timestamp"]).total_seconds()
            > (self.max_age_hours * 3600)
        ]
        for key in expired_keys:
            del self.cache[key]

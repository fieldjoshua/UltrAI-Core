"""
Models module initialization.

This module provides access to various model implementations and utilities.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class QualityMetrics:
    """
    Quality metrics for model responses.

    Attributes:
        coherence_score: Score for the coherence of the response
        technical_depth: Score for the technical depth of the response
        strategic_value: Score for the strategic value of the response
        uniqueness: Score for the uniqueness of the response
    """

    coherence_score: float = 0.0
    technical_depth: float = 0.0
    strategic_value: float = 0.0
    uniqueness: float = 0.0

    def average_score(self) -> float:
        """Calculate the average score across all metrics."""
        return (
            self.coherence_score
            + self.technical_depth
            + self.strategic_value
            + self.uniqueness
        ) / 4


@dataclass
class ModelResponse:
    """
    Response from a model.

    Attributes:
        model: The name of the model that generated the response
        content: The content of the response
        prompt: The prompt that generated the response
        timestamp: The time the response was generated
        tokens_used: The number of tokens used
        quality: Quality metrics for the response
    """

    model: str
    content: str
    prompt: str
    timestamp: float
    tokens_used: int = 0
    quality: QualityMetrics = field(default_factory=QualityMetrics)


class ResponseCache:
    """
    Cache for model responses.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize the response cache.

        Args:
            max_size: Maximum number of items to store in the cache
        """
        self.cache: Dict[str, ModelResponse] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[ModelResponse]:
        """
        Get a response from the cache.

        Args:
            key: The cache key

        Returns:
            The cached response, or None if not found
        """
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, key: str, response: ModelResponse) -> None:
        """
        Add a response to the cache.

        Args:
            key: The cache key
            response: The response to cache
        """
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            self.cache.pop(oldest_key)
        self.cache[key] = response

    def clear_expired(self) -> None:
        """Clear expired cache entries."""
        # In a more sophisticated implementation, we would check timestamps
        # and remove entries older than a certain time
        pass

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get cache metrics.

        Returns:
            Dictionary with cache metrics
        """
        total = self.hits + self.misses
        hit_ratio = self.hits / total if total > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": hit_ratio,
        }

"""
Quality metrics for evaluating and ranking LLM responses

This module provides tools to evaluate the quality of LLM responses
based on various criteria such as relevance, coherence, informativeness,
and factual accuracy.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class QualityMetrics:
    """
    Service for evaluating the quality of LLM responses

    This implements simple heuristic scoring now, but could be enhanced to:
    1. Use model-based evaluation (have one model evaluate another)
    2. Use external benchmarks or reference data
    3. Implement more sophisticated metrics
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        evaluation_model: Optional[Tuple[str, Any]] = None,
    ):
        """
        Initialize quality metrics service

        Args:
            weights: Dictionary mapping metric names to their weights
            evaluation_model: Optional model to use for evaluation (name, adapter)
        """
        self.weights = weights or {
            "length": 0.2,
            "coherence": 0.3,
            "specificity": 0.4,
            "confidence": 0.1,
        }

        # Normalize weights to sum to 1.0
        weight_sum = sum(self.weights.values())
        if weight_sum != 1.0:
            self.weights = {k: v / weight_sum for k, v in self.weights.items()}

        self.evaluation_model = evaluation_model

    async def evaluate(self, prompt: str, response: str, model_name: str) -> float:
        """
        Evaluate the quality of a response using various metrics

        Args:
            prompt: Original prompt
            response: Model response
            model_name: Name of the model that generated the response

        Returns:
            Quality score (0.0 to 1.0, higher is better)
        """
        # If we have an evaluation model, use it for sophisticated evaluation
        if self.evaluation_model:
            return await self._model_based_evaluation(prompt, response)

        # Otherwise, use simple heuristic scoring
        return self._heuristic_evaluation(prompt, response)

    def _heuristic_evaluation(self, prompt: str, response: str) -> float:
        """
        Use simple heuristics to evaluate response quality

        Returns a score from 0.0 to 1.0, higher is better
        """
        scores = {}

        # Length score (0-1): Longer responses up to a point are better
        # Cap at 1500 chars (responses beyond this don't get extra points)
        length = len(response)
        max_favorable_length = 1500
        scores["length"] = min(length / max_favorable_length, 1.0)

        # Coherence score (0-1): Based on paragraph structure, sentence flow
        # Count paragraphs and well-formed sentences
        paragraphs = [p for p in response.split("\n\n") if p.strip()]
        sentences = re.findall(r"[A-Z][^.!?]*[.!?]", response)

        # More paragraphs and sentences suggest better structure (up to a point)
        paragraph_score = min(len(paragraphs) / 3, 1.0)
        sentence_score = min(len(sentences) / 10, 1.0)
        scores["coherence"] = (paragraph_score + sentence_score) / 2

        # Specificity score (0-1): Based on presence of specific details
        # Count numbers, proper nouns, dates, technical terms
        num_numbers = len(re.findall(r"\d+", response))
        num_proper_nouns = len(re.findall(r"[A-Z][a-z]+", response))
        num_dates = len(
            re.findall(
                r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b \d{1,2},? \d{4}",
                response,
            )
        )

        # More specific details suggest higher quality
        specificity_score = min((num_numbers + num_proper_nouns + num_dates) / 20, 1.0)
        scores["specificity"] = specificity_score

        # Confidence score (0-1): Lack of hedge words suggests confidence
        # Count hedge words and phrases
        hedge_patterns = [
            r"\bmight\b",
            r"\bcould\b",
            r"\bperhaps\b",
            r"\bpossibly\b",
            r"\bseem[s]?\b",
            r"\bappear[s]?\b",
            r"\bmaybe\b",
            r"\bprobably\b",
            r"I think",
            r"I believe",
            r"In my opinion",
            r"not sure",
            r"not certain",
            r"it depends",
        ]

        hedge_count = sum(
            len(re.findall(pattern, response, re.IGNORECASE))
            for pattern in hedge_patterns
        )

        # Fewer hedge words suggest more confidence (up to a point)
        confidence_score = max(1.0 - (hedge_count / 10), 0.0)
        scores["confidence"] = confidence_score

        # Combine scores using weights
        final_score = sum(
            scores[metric] * weight for metric, weight in self.weights.items()
        )

        logger.debug(f"Quality scores for response: {scores}, final: {final_score:.2f}")
        return final_score

    async def _model_based_evaluation(self, prompt: str, response: str) -> float:
        """
        Use another model to evaluate the quality of the response

        Currently a placeholder for more sophisticated evaluation
        """
        # This would use the evaluation model to score the response
        # model_name, adapter = self.evaluation_model

        # For now, fall back to heuristic evaluation
        logger.warning("Model-based evaluation not implemented, using heuristics")
        return self._heuristic_evaluation(prompt, response)

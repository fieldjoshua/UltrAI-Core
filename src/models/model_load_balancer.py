"""
Model Load Balancer Module.

This module provides intelligent request routing for LLM models based on
performance, health status, and current load patterns.
"""

import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from collections import defaultdict, deque
import threading
from datetime import datetime, timedelta
import math
import statistics


class ModelHealth(Enum):
    """Health status of a model."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    CRITICAL = "critical"


class RoutingStrategy(Enum):
    """Strategy for routing requests to models."""

    WEIGHTED = "weighted"  # Based on configured weights
    PERFORMANCE = "performance"  # Based on response time and success rate
    ROUND_ROBIN = "round_robin"  # Evenly distribute across all models
    LEAST_LOADED = "least_loaded"  # Route to least loaded model
    ADAPTIVE = "adaptive"  # Automatically adjust based on real-time metrics


@dataclass
class ModelMetrics:
    """Performance metrics for a model."""

    success_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)
    last_success_time: float = 0.0
    last_error_time: float = 0.0
    concurrent_requests: int = 0
    total_requests: int = 0
    health: ModelHealth = ModelHealth.UNKNOWN
    error_types: Dict[str, int] = field(default_factory=dict)
    last_success: Optional[datetime] = None
    last_error: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.error_count
        return self.success_count / total if total > 0 else 1.0

    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        total = self.success_count + self.error_count
        return self.error_count / total if total > 0 else 0.0

    @property
    def health_status(self) -> ModelHealth:
        """Determine health status based on metrics."""
        if self.error_rate > 0.5:  # More than 50% errors
            return ModelHealth.UNHEALTHY
        elif self.error_rate > 0.2:  # More than 20% errors
            return ModelHealth.DEGRADED
        else:
            return ModelHealth.HEALTHY

    def update_response_time(self, time_ms: float) -> None:
        """Update average response time with a new measurement."""
        self.response_times.append(time_ms)

        # Keep only the last 100 measurements
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]

        # Recalculate average
        self.avg_response_time = sum(self.response_times) / len(self.response_times)

    def record_success(self, response_time_ms: float) -> None:
        """Record a successful request."""
        self.success_count += 1
        self.total_requests += 1
        self.last_success_time = time.time()
        self.update_response_time(response_time_ms)
        self.concurrent_requests = max(0, self.concurrent_requests - 1)

    def record_error(self) -> None:
        """Record a failed request."""
        self.error_count += 1
        self.total_requests += 1
        self.last_error_time = time.time()
        self.concurrent_requests = max(0, self.concurrent_requests - 1)

    def record_request_start(self) -> None:
        """Record the start of a new request."""
        self.concurrent_requests += 1

    def determine_health(self) -> ModelHealth:
        """Determine the health status of the model based on error rate."""
        if self.total_requests == 0:
            return ModelHealth.UNKNOWN

        error_rate = self.error_count / self.total_requests

        if error_rate >= 0.5:
            return ModelHealth.CRITICAL

        if error_rate >= 0.25:
            return ModelHealth.DEGRADED

        return ModelHealth.HEALTHY


class ModelLoadBalancer:
    """
    Intelligent load balancer for routing requests to LLM models.

    Features:
    - Health-aware routing based on error rates and response times
    - Load-aware distribution to optimize throughput
    - Adaptive weighting based on real-time performance
    - Support for various routing strategies
    - Automatic failover to healthy models
    """

    def __init__(
        self,
        default_strategy: RoutingStrategy = RoutingStrategy.ADAPTIVE,
        health_check_interval: int = 60,  # seconds
        performance_window: int = 3600,  # 1 hour window for metrics
        max_concurrent_per_model: int = 5,
    ):
        """
        Initialize the load balancer.

        Args:
            default_strategy: Default routing strategy
            health_check_interval: Interval between health checks in seconds
            performance_window: Time window for performance metrics in seconds
            max_concurrent_per_model: Maximum concurrent requests per model
        """
        self.logger = logging.getLogger(__name__)
        self.default_strategy = default_strategy
        self.health_check_interval = health_check_interval
        self.performance_window = performance_window
        self.max_concurrent_per_model = max_concurrent_per_model

        # Model registrations and metrics
        self.model_weights: Dict[str, float] = {}
        self.model_metrics: Dict[str, ModelMetrics] = {}
        self.model_capabilities: Dict[str, Dict[str, Any]] = {}

        # For round-robin routing
        self.round_robin_index = 0

        # For adaptive routing
        self.dynamic_weights: Dict[str, float] = {}
        self.last_weight_update = time.time()
        self.weight_update_interval = 300  # 5 minutes

        # For health checks
        self.last_health_check = time.time()
        self.unhealthy_models: Set[str] = set()

        self.logger.info(
            f"Model load balancer initialized with strategy: {default_strategy.value}"
        )

    def register_model(
        self,
        model_name: str,
        weight: float = 1.0,
        capabilities: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a model with the load balancer.

        Args:
            model_name: Name of the model
            weight: Weight for weighted routing
            capabilities: Optional capabilities dictionary
        """
        self.model_weights[model_name] = weight
        self.dynamic_weights[model_name] = weight
        self.model_metrics[model_name] = ModelMetrics()
        self.model_capabilities[model_name] = capabilities or {}

        self.logger.info(f"Registered model {model_name} with weight {weight}")

    def unregister_model(self, model_name: str) -> None:
        """
        Unregister a model from the load balancer.

        Args:
            model_name: Name of the model
        """
        if model_name in self.model_weights:
            self.model_weights.pop(model_name)
            self.dynamic_weights.pop(model_name)
            self.model_metrics.pop(model_name)
            self.model_capabilities.pop(model_name)

            # Remove from unhealthy models if present
            self.unhealthy_models.discard(model_name)

            self.logger.info(f"Unregistered model {model_name}")

    def update_model_weight(self, model_name: str, weight: float) -> None:
        """
        Update the weight of a model.

        Args:
            model_name: Name of the model
            weight: New weight
        """
        if model_name in self.model_weights:
            self.model_weights[model_name] = weight
            # Also update dynamic weight
            self.dynamic_weights[model_name] = weight

            self.logger.info(f"Updated weight for model {model_name} to {weight}")

    def record_model_success(self, model_name: str, response_time_ms: float) -> None:
        """
        Record a successful request to a model.

        Args:
            model_name: Name of the model
            response_time_ms: Response time in milliseconds
        """
        if model_name in self.model_metrics:
            # Remove from unhealthy models if present
            self.unhealthy_models.discard(model_name)

            # Update metrics
            self.model_metrics[model_name].record_success(response_time_ms)

            self.logger.debug(
                f"Recorded success for model {model_name} "
                f"({response_time_ms:.2f}ms)"
            )

    def record_model_error(self, model_name: str) -> None:
        """
        Record a failed request to a model.

        Args:
            model_name: Name of the model
        """
        if model_name in self.model_metrics:
            # Update metrics
            self.model_metrics[model_name].record_error()

            # Check if model is now unhealthy
            if self.model_metrics[model_name].health_status == ModelHealth.UNHEALTHY:
                self.unhealthy_models.add(model_name)
                self.logger.warning(f"Model {model_name} marked as unhealthy")

            self.logger.debug(f"Recorded error for model {model_name}")

    def record_request_start(self, model_name: str) -> None:
        """
        Record the start of a request to a model.

        Args:
            model_name: Name of the model
        """
        if model_name in self.model_metrics:
            self.model_metrics[model_name].record_request_start()

    def _check_health(self) -> None:
        """Check health of all models and update health status."""
        current_time = time.time()

        # Only check periodically
        if current_time - self.last_health_check < self.health_check_interval:
            return

        self.last_health_check = current_time
        unhealthy_count = 0

        for model_name, metrics in self.model_metrics.items():
            health = metrics.health_status

            if health == ModelHealth.UNHEALTHY:
                self.unhealthy_models.add(model_name)
                unhealthy_count += 1
                self.logger.warning(f"Health check: Model {model_name} is unhealthy")
            elif health == ModelHealth.DEGRADED:
                self.logger.info(f"Health check: Model {model_name} is degraded")
            else:
                # Remove from unhealthy models if present
                self.unhealthy_models.discard(model_name)

        self.logger.info(
            f"Health check completed: {unhealthy_count} unhealthy models out of "
            f"{len(self.model_metrics)}"
        )

    def _update_dynamic_weights(self) -> None:
        """Update dynamic weights based on performance metrics."""
        current_time = time.time()

        # Only update periodically
        if current_time - self.last_weight_update < self.weight_update_interval:
            return

        self.last_weight_update = current_time

        # Skip if we have no models with metrics
        if not self.model_metrics:
            return

        # Calculate performance scores
        performance_scores = {}

        for model_name, metrics in self.model_metrics.items():
            # Skip models with no requests
            if metrics.total_requests == 0:
                performance_scores[model_name] = 1.0
                continue

            # Calculate score based on success rate and response time
            # Higher success rate and lower response time = better score
            success_factor = metrics.success_rate**2  # Square to penalize errors more

            # Normalize response time (lower is better)
            # Add small value to avoid division by zero
            response_time_ms = metrics.avg_response_time
            if response_time_ms <= 0:
                response_time_ms = 1  # Minimum value

            # Response time factor (inverse, normalized between 0-1)
            # Using log scale to handle wide range of response times
            # 100ms -> ~0.8, 500ms -> ~0.6, 1000ms -> ~0.5, 3000ms -> ~0.3
            time_factor = 1.0 / (1.0 + 0.7 * (response_time_ms / 1000))

            # Combined score
            score = success_factor * time_factor

            # Apply current load as a multiplier
            # Higher concurrent requests = lower score
            load_factor = max(
                0.5, 1.0 - (metrics.concurrent_requests / self.max_concurrent_per_model)
            )

            final_score = score * load_factor

            # Store score
            performance_scores[model_name] = final_score

        # Normalize scores into weights
        total_score = sum(performance_scores.values())

        if total_score > 0:
            # Convert scores to weights (ensure minimum weight of 0.1)
            for model_name, score in performance_scores.items():
                base_weight = self.model_weights.get(model_name, 1.0)
                performance_weight = max(0.1, score / total_score)

                # Blend base weight with performance weight (70% performance, 30% base)
                self.dynamic_weights[model_name] = (
                    0.7 * performance_weight + 0.3 * base_weight
                )

        self.logger.info("Updated dynamic weights based on performance metrics")

    def _get_models_for_weighted_routing(
        self, candidates: List[str], required_count: int
    ) -> List[str]:
        """
        Get models using weighted routing strategy.

        Args:
            candidates: List of candidate models
            required_count: Number of models to return

        Returns:
            List of selected models
        """
        # Handle edge cases
        if not candidates:
            return []

        if len(candidates) <= required_count:
            return candidates

        # Get weights for candidates
        weights = [self.dynamic_weights.get(model, 1.0) for model in candidates]

        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            # Equal weights if total is zero
            weights = [1.0 / len(candidates)] * len(candidates)

        # Select models based on weights
        selected = []

        # Always include the highest weighted model
        max_index = weights.index(max(weights))
        selected.append(candidates[max_index])

        # Select remaining models with probability proportional to weight
        remaining_candidates = [c for i, c in enumerate(candidates) if i != max_index]
        remaining_weights = [w for i, w in enumerate(weights) if i != max_index]

        # Normalize remaining weights
        total_remaining = sum(remaining_weights)
        if total_remaining > 0:
            remaining_weights = [w / total_remaining for w in remaining_weights]

        # Select the rest using weighted random
        while len(selected) < required_count and remaining_candidates:
            if not remaining_weights:
                break

            # Select based on weights
            index = random.choices(
                range(len(remaining_candidates)), weights=remaining_weights, k=1
            )[0]

            selected.append(remaining_candidates[index])

            # Remove selected model from remaining
            remaining_candidates.pop(index)
            remaining_weights.pop(index)

        return selected

    def _get_models_for_performance_routing(
        self, candidates: List[str], required_count: int
    ) -> List[str]:
        """
        Get models using performance-based routing strategy.

        Args:
            candidates: List of candidate models
            required_count: Number of models to return

        Returns:
            List of selected models
        """
        if not candidates:
            return []

        if len(candidates) <= required_count:
            return candidates

        # Sort by performance score (success rate and response time)
        scored_models = []

        for model in candidates:
            metrics = self.model_metrics.get(model)
            if not metrics:
                # If no metrics, give neutral score
                scored_models.append((model, 0.5))
                continue

            # Calculate score
            success_score = metrics.success_rate

            # Response time score (lower is better)
            time_ms = metrics.avg_response_time
            time_score = 1.0 / (1.0 + 0.5 * (time_ms / 1000)) if time_ms > 0 else 0.5

            # Combined score
            combined_score = 0.7 * success_score + 0.3 * time_score
            scored_models.append((model, combined_score))

        # Sort by score (descending)
        scored_models.sort(key=lambda x: x[1], reverse=True)

        # Return top models
        return [model for model, _ in scored_models[:required_count]]

    def _get_models_for_round_robin(
        self, candidates: List[str], required_count: int
    ) -> List[str]:
        """
        Get models using round-robin routing strategy.

        Args:
            candidates: List of candidate models
            required_count: Number of models to return

        Returns:
            List of selected models
        """
        if not candidates:
            return []

        if len(candidates) <= required_count:
            return candidates

        # Get starting index for round-robin
        start_idx = self.round_robin_index % len(candidates)

        # Increment for next time
        self.round_robin_index += 1

        # Wrap around the list
        selected = (candidates[start_idx:] + candidates[:start_idx])[:required_count]

        return selected

    def _get_models_for_least_loaded(
        self, candidates: List[str], required_count: int
    ) -> List[str]:
        """
        Get models with the lowest current load.

        Args:
            candidates: List of candidate models
            required_count: Number of models to return

        Returns:
            List of selected models
        """
        if not candidates:
            return []

        if len(candidates) <= required_count:
            return candidates

        # Sort by concurrent requests (ascending)
        sorted_models = sorted(
            candidates,
            key=lambda m: self.model_metrics.get(m, ModelMetrics()).concurrent_requests,
        )

        return sorted_models[:required_count]

    def get_models_for_request(
        self,
        required_count: int = 1,
        candidates: Optional[List[str]] = None,
        strategy: Optional[RoutingStrategy] = None,
        required_capabilities: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Get models to handle a request based on current strategy.

        Args:
            required_count: Number of models to return
            candidates: Optional list of candidate models
            strategy: Optional override for routing strategy
            required_capabilities: Optional map of required capabilities

        Returns:
            List of model names to use for the request
        """
        # Update health status and dynamic weights
        self._check_health()
        self._update_dynamic_weights()

        # Use all registered models if no candidates provided
        if candidates is None:
            candidates = list(self.model_weights.keys())

        # Filter out unhealthy models
        healthy_candidates = [
            model for model in candidates if model not in self.unhealthy_models
        ]

        # Filter by required capabilities if specified
        if required_capabilities:
            capability_candidates = []
            for model in healthy_candidates:
                capabilities = self.model_capabilities.get(model, {})
                meets_requirements = True

                for key, value in required_capabilities.items():
                    if capabilities.get(key) != value:
                        meets_requirements = False
                        break

                if meets_requirements:
                    capability_candidates.append(model)

            healthy_candidates = capability_candidates

        # If no healthy candidates, use the original set as fallback
        if not healthy_candidates and candidates:
            self.logger.warning(
                "No healthy models available, using all candidates as fallback"
            )
            healthy_candidates = candidates

        # If no candidates at all, return empty list
        if not healthy_candidates:
            return []

        # Use default strategy if none specified
        strategy = strategy or self.default_strategy

        # Apply the selected strategy
        if strategy == RoutingStrategy.WEIGHTED:
            return self._get_models_for_weighted_routing(
                healthy_candidates, required_count
            )
        elif strategy == RoutingStrategy.PERFORMANCE:
            return self._get_models_for_performance_routing(
                healthy_candidates, required_count
            )
        elif strategy == RoutingStrategy.ROUND_ROBIN:
            return self._get_models_for_round_robin(healthy_candidates, required_count)
        elif strategy == RoutingStrategy.LEAST_LOADED:
            return self._get_models_for_least_loaded(healthy_candidates, required_count)
        elif strategy == RoutingStrategy.ADAPTIVE:
            # Adaptive strategy uses a mix of performance and load
            # First, filter by performance
            performance_candidates = self._get_models_for_performance_routing(
                healthy_candidates, min(required_count * 2, len(healthy_candidates))
            )

            # Then select by load from those candidates
            return self._get_models_for_least_loaded(
                performance_candidates, required_count
            )

        # Default to performance-based routing
        return self._get_models_for_performance_routing(
            healthy_candidates, required_count
        )

    def get_optimal_models(
        self,
        required_count: int = 1,
        candidates: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Get the optimal models based on current conditions.

        This is a convenience method that uses the adaptive strategy.

        Args:
            required_count: Number of models to return
            candidates: Optional list of candidate models

        Returns:
            List of model names to use for the request
        """
        return self.get_models_for_request(
            required_count=required_count,
            candidates=candidates,
            strategy=RoutingStrategy.ADAPTIVE,
        )

    def get_model_metrics(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get current metrics for a model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with metrics or None if model not found
        """
        if model_name not in self.model_metrics:
            return None

        metrics = self.model_metrics[model_name]

        return {
            "success_count": metrics.success_count,
            "error_count": metrics.error_count,
            "success_rate": metrics.success_rate,
            "avg_response_time_ms": metrics.avg_response_time,
            "concurrent_requests": metrics.concurrent_requests,
            "health_status": metrics.health_status.value,
            "dynamic_weight": self.dynamic_weights.get(model_name, 1.0),
            "base_weight": self.model_weights.get(model_name, 1.0),
        }

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all models.

        Returns:
            Dictionary mapping model names to metrics
        """
        return {
            model: self.get_model_metrics(model) or {}
            for model in self.model_weights.keys()
        }

    def record_success(self, model_id: str, response_time: float, tokens: int = 0) -> None:
        """Record a successful model request and update metrics."""
        with self._lock:
            if model_id not in self.model_metrics:
                logging.warning("Attempted to record success for unregistered model %s", model_id)
                return

            metrics = self.model_metrics[model_id]
            metrics.success_count += 1
            metrics.total_requests += 1
            metrics.token_count += tokens

            # Update response time tracking
            metrics.response_times.append(response_time)
            if len(metrics.response_times) > 100:
                metrics.response_times.popleft()

            # Update health status
            metrics.health = metrics.determine_health()

            # Record the timestamp of the last successful request
            metrics.last_success = datetime.now()

            logging.debug("Recorded successful request for model %s with response time %.2f",
                         model_id, response_time)

            # Update dynamic weights if using performance-based routing
            if self.default_strategy in (RoutingStrategy.PERFORMANCE, RoutingStrategy.ADAPTIVE):
                self._update_dynamic_weights()

    def record_error(self, model_id: str, error_type: str = "general") -> None:
        """Record a model request error and update metrics."""
        with self._lock:
            if model_id not in self.model_metrics:
                logging.warning("Attempted to record error for unregistered model %s", model_id)
                return

            metrics = self.model_metrics[model_id]
            metrics.error_count += 1
            metrics.total_requests += 1

            # Track error types
            metrics.error_types[error_type] += 1

            # Update health status
            old_health = metrics.health
            metrics.health = metrics.determine_health()

            # Record the timestamp of the last error
            metrics.last_error = datetime.now()

            # Log health degradation
            if old_health != metrics.health and metrics.health in (ModelHealth.DEGRADED, ModelHealth.CRITICAL):
                logging.warning("Model %s health degraded to %s (error rate: %.2f%%)",
                               model_id, metrics.health.name,
                               (metrics.error_count / metrics.total_requests) * 100)

            # Update dynamic weights if using performance-based routing
            if self.default_strategy in (RoutingStrategy.PERFORMANCE, RoutingStrategy.ADAPTIVE):
                self._update_dynamic_weights()

            # Check if we need to circuit-break this model
            self._check_circuit_breaker(model_id)

    def _update_performance_weights(self) -> None:
        """Update weights based on model performance metrics."""
        if not self.model_metrics:
            return

        total_weight = 0
        for model_id, metrics in self.model_metrics.items():
            # Skip models that are in critical health
            if metrics.health == ModelHealth.CRITICAL:
                self.dynamic_weights[model_id] = 0
                continue

            # Calculate average response time
            if metrics.response_times:

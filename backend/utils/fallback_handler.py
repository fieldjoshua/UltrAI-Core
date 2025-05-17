"""Fallback handler for API failures.

This module provides fallback mechanisms for when primary services fail,
including cached responses, default values, and alternative providers.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union

from .circuit_breaker import CircuitOpenError
from .retry_handler import RetryError

logger = logging.getLogger(__name__)


@dataclass
class FallbackConfig:
    """Configuration for fallback behavior."""

    cache_ttl: int = 300  # seconds
    use_cache: bool = True
    use_defaults: bool = True
    use_alternative_providers: bool = True
    degrade_gracefully: bool = True
    fallback_order: List[str] = None  # Order of fallback strategies


class FallbackStrategy(ABC):
    """Abstract base class for fallback strategies."""

    @abstractmethod
    async def handle(self, context: Dict[str, Any]) -> Any:
        """Handle the fallback scenario."""
        pass


class CachedResponseStrategy(FallbackStrategy):
    """Use cached response as fallback."""

    def __init__(self, cache_service, ttl: int = 300):
        """Initialize with cache service."""
        self.cache_service = cache_service
        self.ttl = ttl

    async def handle(self, context: Dict[str, Any]) -> Any:
        """Return cached response if available."""
        cache_key = context.get("cache_key")
        if not cache_key:
            return None

        cached_value = await self.cache_service.get(cache_key)
        if cached_value:
            logger.info(f"Using cached response for key: {cache_key}")
            return cached_value

        return None


class DefaultValueStrategy(FallbackStrategy):
    """Return default values as fallback."""

    def __init__(self, defaults: Dict[str, Any]):
        """Initialize with default values."""
        self.defaults = defaults

    async def handle(self, context: Dict[str, Any]) -> Any:
        """Return appropriate default value."""
        operation = context.get("operation")
        if operation in self.defaults:
            logger.info(f"Using default value for operation: {operation}")
            return self.defaults[operation]

        # Generic default based on expected type
        expected_type = context.get("expected_type")
        if expected_type == "list":
            return []
        elif expected_type == "dict":
            return {}
        elif expected_type == "str":
            return ""
        elif expected_type == "bool":
            return False
        elif expected_type == "int":
            return 0

        return None


class AlternativeProviderStrategy(FallbackStrategy):
    """Try alternative service providers as fallback."""

    def __init__(self, providers: List[Dict[str, Any]]):
        """Initialize with list of alternative providers."""
        self.providers = providers

    async def handle(self, context: Dict[str, Any]) -> Any:
        """Try alternative providers in order."""
        failed_provider = context.get("failed_provider")
        operation = context.get("operation")

        for provider in self.providers:
            if provider["name"] == failed_provider:
                continue  # Skip the failed provider

            try:
                handler = provider["handler"]
                result = await handler(operation, context.get("params", {}))
                logger.info(f"Fallback successful with provider: {provider['name']}")
                return result
            except Exception as e:
                logger.warning(f"Fallback provider {provider['name']} failed: {str(e)}")
                continue

        return None


class DegradedServiceStrategy(FallbackStrategy):
    """Provide degraded but functional service."""

    def __init__(self, degraded_handlers: Dict[str, Callable]):
        """Initialize with degraded operation handlers."""
        self.degraded_handlers = degraded_handlers

    async def handle(self, context: Dict[str, Any]) -> Any:
        """Provide degraded functionality."""
        operation = context.get("operation")

        if operation in self.degraded_handlers:
            handler = self.degraded_handlers[operation]
            result = await handler(context)
            logger.info(f"Providing degraded service for: {operation}")
            return result

        return None


class FallbackHandler:
    """Main fallback handler coordinating different strategies."""

    def __init__(self, config: FallbackConfig):
        """Initialize fallback handler."""
        self.config = config
        self.strategies: Dict[str, FallbackStrategy] = {}
        self.stats = {
            "primary_failures": 0,
            "fallback_successes": 0,
            "total_fallbacks": 0,
        }

    def register_strategy(self, name: str, strategy: FallbackStrategy):
        """Register a fallback strategy."""
        self.strategies[name] = strategy
        logger.info(f"Registered fallback strategy: {name}")

    async def handle_failure(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Handle failure with fallback strategies."""
        self.stats["primary_failures"] += 1
        self.stats["total_fallbacks"] += 1

        logger.warning(
            f"Primary service failed: {str(error)}. "
            f"Attempting fallback for operation: {context.get('operation')}"
        )

        # Determine fallback order
        fallback_order = self.config.fallback_order or list(self.strategies.keys())

        for strategy_name in fallback_order:
            if strategy_name not in self.strategies:
                continue

            strategy = self.strategies[strategy_name]

            try:
                result = await strategy.handle(context)
                if result is not None:
                    self.stats["fallback_successes"] += 1
                    logger.info(f"Fallback successful using strategy: {strategy_name}")
                    return result
            except Exception as e:
                logger.error(f"Fallback strategy {strategy_name} failed: {str(e)}")
                continue

        # All fallbacks failed
        raise FallbackExhaustedError(
            f"All fallback strategies failed for operation: {context.get('operation')}",
            original_error=error,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get fallback statistics."""
        return {
            **self.stats,
            "success_rate": (
                self.stats["fallback_successes"] / self.stats["total_fallbacks"]
                if self.stats["total_fallbacks"] > 0
                else 0
            ),
        }


class FallbackExhaustedError(Exception):
    """Raised when all fallback options are exhausted."""

    def __init__(self, message: str, original_error: Exception):
        super().__init__(message)
        self.original_error = original_error


def with_fallback(fallback_handler: FallbackHandler, context_builder: Callable = None):
    """Decorator to add fallback handling to functions."""

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (CircuitOpenError, RetryError, Exception) as e:
                # Build context for fallback
                context = {
                    "operation": func.__name__,
                    "args": args,
                    "kwargs": kwargs,
                    "error": str(e),
                }

                if context_builder:
                    additional_context = context_builder(*args, **kwargs)
                    context.update(additional_context)

                return await fallback_handler.handle_failure(e, context)

        return wrapper

    return decorator


class SmartFallbackHandler(FallbackHandler):
    """Enhanced fallback handler with learning capabilities."""

    def __init__(self, config: FallbackConfig):
        """Initialize smart fallback handler."""
        super().__init__(config)
        self.fallback_history: List[Dict[str, Any]] = []
        self.strategy_performance: Dict[str, Dict[str, int]] = {}

    async def handle_failure(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Handle failure with smart strategy selection."""
        # Record failure
        failure_record = {
            "timestamp": datetime.now(),
            "operation": context.get("operation"),
            "error_type": type(error).__name__,
            "context": context,
        }

        # Use performance data to reorder strategies
        fallback_order = self._optimize_strategy_order(context)

        for strategy_name in fallback_order:
            if strategy_name not in self.strategies:
                continue

            strategy = self.strategies[strategy_name]

            try:
                result = await strategy.handle(context)
                if result is not None:
                    # Record success
                    self._record_strategy_success(strategy_name, context)
                    failure_record["successful_strategy"] = strategy_name
                    self.fallback_history.append(failure_record)
                    return result
            except Exception as e:
                # Record failure
                self._record_strategy_failure(strategy_name, context)
                continue

        # All fallbacks failed
        failure_record["all_strategies_failed"] = True
        self.fallback_history.append(failure_record)

        raise FallbackExhaustedError(
            f"All fallback strategies failed for operation: {context.get('operation')}",
            original_error=error,
        )

    def _optimize_strategy_order(self, context: Dict[str, Any]) -> List[str]:
        """Optimize strategy order based on past performance."""
        operation = context.get("operation", "default")

        # Get performance data for this operation
        performances = []
        for strategy_name in self.strategies:
            perf_key = f"{operation}:{strategy_name}"
            if perf_key in self.strategy_performance:
                perf = self.strategy_performance[perf_key]
                success_rate = perf["successes"] / (
                    perf["successes"] + perf["failures"]
                )
                performances.append((strategy_name, success_rate))
            else:
                performances.append((strategy_name, 0.5))  # Default 50% for unknown

        # Sort by success rate (descending)
        performances.sort(key=lambda x: x[1], reverse=True)

        return [name for name, _ in performances]

    def _record_strategy_success(self, strategy_name: str, context: Dict[str, Any]):
        """Record successful strategy execution."""
        operation = context.get("operation", "default")
        perf_key = f"{operation}:{strategy_name}"

        if perf_key not in self.strategy_performance:
            self.strategy_performance[perf_key] = {"successes": 0, "failures": 0}

        self.strategy_performance[perf_key]["successes"] += 1

    def _record_strategy_failure(self, strategy_name: str, context: Dict[str, Any]):
        """Record failed strategy execution."""
        operation = context.get("operation", "default")
        perf_key = f"{operation}:{strategy_name}"

        if perf_key not in self.strategy_performance:
            self.strategy_performance[perf_key] = {"successes": 0, "failures": 0}

        self.strategy_performance[perf_key]["failures"] += 1

    def get_insights(self) -> Dict[str, Any]:
        """Get insights about fallback performance."""
        return {
            "total_fallbacks": len(self.fallback_history),
            "strategy_performance": self.strategy_performance,
            "recent_failures": self.fallback_history[-10:],
            "most_successful_strategies": self._get_top_strategies(),
            "operations_with_most_failures": self._get_problematic_operations(),
        }

    def _get_top_strategies(self) -> List[Dict[str, Any]]:
        """Get most successful strategies across all operations."""
        strategy_totals = {}

        for perf_key, perf_data in self.strategy_performance.items():
            _, strategy_name = perf_key.split(":", 1)

            if strategy_name not in strategy_totals:
                strategy_totals[strategy_name] = {"successes": 0, "failures": 0}

            strategy_totals[strategy_name]["successes"] += perf_data["successes"]
            strategy_totals[strategy_name]["failures"] += perf_data["failures"]

        # Calculate success rates
        strategies_with_rates = []
        for name, totals in strategy_totals.items():
            total = totals["successes"] + totals["failures"]
            if total > 0:
                success_rate = totals["successes"] / total
                strategies_with_rates.append(
                    {
                        "strategy": name,
                        "success_rate": success_rate,
                        "total_attempts": total,
                    }
                )

        # Sort by success rate
        strategies_with_rates.sort(key=lambda x: x["success_rate"], reverse=True)

        return strategies_with_rates[:5]  # Top 5

    def _get_problematic_operations(self) -> List[Dict[str, Any]]:
        """Get operations with most failures."""
        operation_failures = {}

        for record in self.fallback_history:
            operation = record.get("operation", "unknown")

            if operation not in operation_failures:
                operation_failures[operation] = {"failures": 0, "successes": 0}

            if record.get("all_strategies_failed"):
                operation_failures[operation]["failures"] += 1
            else:
                operation_failures[operation]["successes"] += 1

        # Convert to list with failure rates
        operations = []
        for operation, counts in operation_failures.items():
            total = counts["failures"] + counts["successes"]
            failure_rate = counts["failures"] / total if total > 0 else 0

            operations.append(
                {
                    "operation": operation,
                    "failure_rate": failure_rate,
                    "total_attempts": total,
                }
            )

        # Sort by failure rate
        operations.sort(key=lambda x: x["failure_rate"], reverse=True)

        return operations[:5]  # Top 5 problematic

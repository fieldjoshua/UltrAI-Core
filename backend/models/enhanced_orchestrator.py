"""
Enhanced Orchestrator Facade Module

This module simply re-exports the EnhancedOrchestrator from the src module
to make it available in the backend.
"""

import logging
import os
import sys
from typing import Dict, Optional

# Configure logger
logger = logging.getLogger(__name__)

# Try to import from src
try:
    # Add src to path if needed
    src_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "src")
    )
    if src_path not in sys.path:
        sys.path.append(src_path)

    # Import the actual orchestrator
    from src.models.enhanced_orchestrator import (
        AnalysisMode,
        EnhancedOrchestrator,
        OrchestratorConfig,
    )

    # Note: We're keeping this as src.models because this is a facade that intentionally
    # imports from the src directory

    logger.info("Successfully imported EnhancedOrchestrator from src")
except ImportError as e:
    logger.warning(f"Could not import EnhancedOrchestrator from src: {e}")

    # Create stub classes for when the actual implementation is not available
    class AnalysisMode:
        """Stub for AnalysisMode"""

        def __init__(
            self,
            name: str,
            pattern: str,
            models: Optional[list] = None,
            model_selection_strategy: str = "weighted",
            evaluate_quality: bool = True,
            cache_responses: bool = True,
            timeout: Optional[float] = None,
        ):
            self.name = name
            self.pattern = pattern
            self.models = models
            self.model_selection_strategy = model_selection_strategy
            self.evaluate_quality = evaluate_quality
            self.cache_responses = cache_responses
            self.timeout = timeout

    class OrchestratorConfig:
        """Stub for OrchestratorConfig"""

        def __init__(
            self,
            cache_enabled: bool = True,
            max_retries: int = 3,
            retry_base_delay: float = 0.5,
            parallel_processing: bool = True,
            max_workers: Optional[int] = None,
            circuit_breaker_enabled: bool = True,
            failure_threshold: int = 5,
            recovery_timeout: int = 60,
            default_pattern: str = "gut",
            default_output_format: str = "plain",
            collect_metrics: bool = True,
            analysis_modes: Optional[Dict[str, "AnalysisMode"]] = None,
        ):
            self.cache_enabled = cache_enabled
            self.max_retries = max_retries
            self.retry_base_delay = retry_base_delay
            self.parallel_processing = parallel_processing
            self.max_workers = max_workers
            self.circuit_breaker_enabled = circuit_breaker_enabled
            self.failure_threshold = failure_threshold
            self.recovery_timeout = recovery_timeout
            self.default_pattern = default_pattern
            self.default_output_format = default_output_format
            self.collect_metrics = collect_metrics
            self.analysis_modes = analysis_modes or {}

    class EnhancedOrchestrator:
        """Stub for EnhancedOrchestrator"""

        def __init__(self, config: Optional[OrchestratorConfig] = None):
            self.config = config or OrchestratorConfig()
            self.model_registry = {}
            self.patterns = {
                "gut": {"name": "gut", "stages": ["initial"]},
                "confidence": {"name": "confidence", "stages": ["initial", "meta"]},
                "perspective": {
                    "name": "perspective",
                    "stages": ["initial", "meta", "hyper"],
                },
            }
            self.circuit_breakers = _CircuitBreakerRegistry()

    class _CircuitBreakerRegistry:
        """Stub for CircuitBreakerRegistry"""

        def __init__(self):
            self._breakers = {}

        def get(self, name):
            return self._breakers.get(name)

        def get_or_create(self, name, failure_threshold=5, recovery_timeout=60):
            if name not in self._breakers:
                self._breakers[name] = _CircuitBreaker(
                    name, failure_threshold, recovery_timeout
                )
            return self._breakers[name]

    class _CircuitBreaker:
        """Stub for CircuitBreaker"""

        def __init__(self, name, failure_threshold, recovery_timeout):
            self.name = name
            self.failure_threshold = failure_threshold
            self.recovery_timeout = recovery_timeout
            self._status = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

        def allow_request(self):
            return self._status != "OPEN"

        def record_success(self):
            self._status = "CLOSED"

        def record_failure(self):
            self._status = "OPEN"

        def expected_recovery_time(self):
            return 60.0  # Fixed 60 seconds for stub

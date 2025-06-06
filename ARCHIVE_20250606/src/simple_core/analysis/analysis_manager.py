"""
Analysis manager for the Simple Core Orchestrator.

This module provides the AnalysisManager class for managing and executing
analysis modules.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type

from .analysis_module import AnalysisModule

logger = logging.getLogger(__name__)


class AnalysisManager:
    """
    Manager for analysis modules.

    This class handles loading, configuring, and executing analysis modules
    for analyzing LLM responses.
    """

    def __init__(
        self,
        enabled_modules: Optional[List[str]] = None,
        weights: Optional[Dict[str, float]] = None,
        module_registry: Optional[Dict[str, Type[AnalysisModule]]] = None,
    ):
        """
        Initialize the analysis manager.

        Args:
            enabled_modules: List of module names to enable (default: ['comparative'])
            weights: Dictionary mapping module names to weights
            module_registry: Dictionary mapping names to module classes
        """
        # Set module registry
        self.module_registry = module_registry or {}

        # Set enabled modules (default to comparative analysis only)
        self.enabled_modules = enabled_modules or ["comparative"]

        # Set default weights (all equal)
        self.weights = weights or {name: 1.0 for name in self.enabled_modules}

        # Instantiate the modules
        self.modules: Dict[str, AnalysisModule] = {}
        for name in self.enabled_modules:
            if name in self.module_registry:
                weight = self.weights.get(name, 1.0)
                self.modules[name] = self.module_registry[name](name, weight)
                logger.info(f"Initialized analysis module: {name} (weight: {weight})")
            else:
                logger.warning(f"Unknown analysis module: {name}")

    async def analyze(
        self,
        prompt: str,
        responses: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze responses using all enabled modules.

        Args:
            prompt: The original prompt
            responses: List of response objects from different models
            options: Optional configuration for analysis

        Returns:
            Dictionary containing aggregated analysis results from all modules
        """
        options = options or {}

        # Process runtime overrides
        enabled_modules = self._get_runtime_modules(options)

        # Run all enabled modules in parallel
        analysis_tasks = []
        for name, module in self.modules.items():
            if name in enabled_modules:
                # Get module options
                module_options = options.get(name, {})

                # Create analysis task
                task = asyncio.create_task(
                    module.analyze(prompt, responses, module_options)
                )
                analysis_tasks.append((name, task))

        # Wait for all analyses to complete
        results = {}
        for name, task in analysis_tasks:
            try:
                result = await task
                results[name] = result
            except Exception as e:
                logger.error(f"Error in analysis module {name}: {str(e)}")
                results[name] = {"error": str(e)}

        # Aggregate results
        aggregated = self._aggregate_results(results, options)

        return aggregated

    def _get_runtime_modules(self, options: Dict[str, Any]) -> List[str]:
        """Get the list of modules to run based on runtime options."""
        # Start with configured modules
        enabled = self.enabled_modules.copy()

        # Apply runtime enable/disable options
        runtime_enable = options.get("enable", [])
        runtime_disable = options.get("disable", [])

        # Add modules to enable
        for module in runtime_enable:
            if module in self.module_registry and module not in enabled:
                enabled.append(module)

        # Remove modules to disable
        enabled = [m for m in enabled if m not in runtime_disable]

        return enabled

    def _aggregate_results(
        self, results: Dict[str, Dict[str, Any]], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate results from multiple analysis modules."""
        # Get runtime weights if provided
        runtime_weights = options.get("weights", {})

        # Calculate normalized weights
        weights = {}
        for name in results:
            # Use runtime weight if provided, otherwise use default
            weights[name] = runtime_weights.get(name, self.weights.get(name, 1.0))

        # Normalize weights to sum to 1.0
        weight_sum = sum(weights.values())
        if weight_sum > 0:
            weights = {k: v / weight_sum for k, v in weights.items()}

        # Build aggregated results
        aggregated = {
            "modules": list(results.keys()),
            "weights": weights,
            "individual_results": results,
            "combined_summary": self._generate_combined_summary(results, weights),
        }

        return aggregated

    def _generate_combined_summary(
        self, results: Dict[str, Dict[str, Any]], weights: Dict[str, float]
    ) -> str:
        """Generate a combined summary from all analysis results."""
        summaries = []

        for name, result in results.items():
            if "summary" in result and isinstance(result["summary"], str):
                weight = weights.get(name, 0)
                summaries.append(
                    f"Analysis from {name} (weight: {weight:.2f}):\n{result['summary']}\n"
                )

        if not summaries:
            return "No analysis summaries available."

        return "\n".join(summaries)

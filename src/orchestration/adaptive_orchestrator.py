"""
AdaptiveOrchestrator module for dynamic, context-aware orchestration.

This module provides the most sophisticated implementation of the BaseOrchestrator,
capable of adapting its strategy based on the context of the request, system load,
and historical performance data.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Set, Callable, Union
from enum import Enum

from src.orchestration.base_orchestrator import BaseOrchestrator
from src.orchestration.simple_orchestrator import OrchestratorResponse
from src.orchestration.parallel_orchestrator import ParallelOrchestrator


logger = logging.getLogger(__name__)


class OrchestrationStrategy(str, Enum):
    """Orchestration strategies that can be used by the AdaptiveOrchestrator."""
    SIMPLE = "simple"  # Send to all providers, analyze, synthesize
    PARALLEL = "parallel"  # Optimized parallel execution with early stopping
    WATERFALL = "waterfall"  # Try providers in sequence until success
    BALANCED = "balanced"  # Balance between quality and efficiency
    ADAPTIVE = "adaptive"  # Automatically select the best strategy for the context
    COST_OPTIMIZED = "cost_optimized"  # Prioritize reducing API costs
    QUALITY_OPTIMIZED = "quality_optimized"  # Prioritize response quality
    SPEED_OPTIMIZED = "speed_optimized"  # Prioritize response speed


class AdaptiveOrchestrator(BaseOrchestrator):
    """
    Advanced orchestrator with adaptive strategy selection:
    1. Dynamic strategy selection based on request context
    2. Learning from historical performance data
    3. Adaptable to changing system conditions
    4. Optimal resource allocation across requests
    
    This implementation represents the most sophisticated orchestration approach,
    combining multiple strategies and adapting to the specific needs of each request.
    """

    def __init__(
        self,
        max_retries: int = 3,
        timeout_seconds: int = 30,
        default_strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE,
        quality_threshold: float = 0.7,
        max_providers_per_request: int = 3,
        learning_rate: float = 0.1
    ):
        """
        Initialize the adaptive orchestrator.
        
        Args:
            max_retries: Maximum number of retries for failed requests
            timeout_seconds: Timeout for LLM requests in seconds
            default_strategy: Default orchestration strategy to use
            quality_threshold: Minimum quality score threshold for responses
            max_providers_per_request: Maximum number of providers to use per request
            learning_rate: Rate at which the orchestrator adapts to new performance data
        """
        super().__init__(
            max_retries=max_retries,
            parallel_requests=True,  # Always use parallel requests
            timeout_seconds=timeout_seconds
        )
        self.default_strategy = default_strategy
        self.quality_threshold = quality_threshold
        self.max_providers_per_request = max_providers_per_request
        self.learning_rate = learning_rate
        self.logger = logging.getLogger("orchestrator.adaptive")
        
        # Initialize performance tracking
        self.provider_scores: Dict[str, Dict[str, float]] = {}
        self.strategy_performance: Dict[str, Dict[str, float]] = {}
        
        # Initialize strategy handlers
        self.strategy_handlers: Dict[OrchestrationStrategy, Callable] = {
            OrchestrationStrategy.SIMPLE: self._strategy_simple,
            OrchestrationStrategy.PARALLEL: self._strategy_parallel,
            OrchestrationStrategy.WATERFALL: self._strategy_waterfall,
            OrchestrationStrategy.BALANCED: self._strategy_balanced,
            OrchestrationStrategy.COST_OPTIMIZED: self._strategy_cost_optimized,
            OrchestrationStrategy.QUALITY_OPTIMIZED: self._strategy_quality_optimized,
            OrchestrationStrategy.SPEED_OPTIMIZED: self._strategy_speed_optimized,
            OrchestrationStrategy.ADAPTIVE: self._strategy_adaptive
        }
        
        # Initialize sub-orchestrators
        self._simple_orchestrator = None
        self._parallel_orchestrator = None
        
        # System state tracking
        self.system_load = 0.0  # 0.0-1.0 scale
        self.request_count = 0
        self.recent_latencies: List[float] = []
    
    def _get_simple_orchestrator(self) -> 'SimpleOrchestrator':
        """Get or create a SimpleOrchestrator instance."""
        from src.orchestration.simple_orchestrator import SimpleOrchestrator
        
        if not self._simple_orchestrator:
            self._simple_orchestrator = SimpleOrchestrator(
                max_retries=self.max_retries,
                parallel_requests=self.parallel_requests,
                timeout_seconds=self.timeout_seconds
            )
            
            # Share providers with the sub-orchestrator
            self._simple_orchestrator.providers = self.providers
            self._simple_orchestrator.provider_configs = self.provider_configs
            self._simple_orchestrator.request_stats = self.request_stats
            
        return self._simple_orchestrator
    
    def _get_parallel_orchestrator(self) -> 'ParallelOrchestrator':
        """Get or create a ParallelOrchestrator instance."""
        from src.orchestration.parallel_orchestrator import ParallelOrchestrator
        
        if not self._parallel_orchestrator:
            self._parallel_orchestrator = ParallelOrchestrator(
                max_retries=self.max_retries,
                timeout_seconds=self.timeout_seconds,
                max_parallel_providers=self.max_providers_per_request
            )
            
            # Share providers with the sub-orchestrator
            self._parallel_orchestrator.providers = self.providers
            self._parallel_orchestrator.provider_configs = self.provider_configs
            self._parallel_orchestrator.request_stats = self.request_stats
            
        return self._parallel_orchestrator
    
    def _update_system_state(self, response_time: float) -> None:
        """
        Update system state tracking with recent request data.
        
        Args:
            response_time: The time taken to process the request
        """
        self.request_count += 1
        
        # Update recent latencies (keep last 100)
        self.recent_latencies.append(response_time)
        if len(self.recent_latencies) > 100:
            self.recent_latencies.pop(0)
            
        # Update system load (simplified model based on recent latencies)
        if self.recent_latencies:
            # Recent average latency compared to timeout
            avg_latency = sum(self.recent_latencies) / len(self.recent_latencies)
            latency_load = min(1.0, avg_latency / self.timeout_seconds)
            
            # Update load with exponential smoothing
            self.system_load = 0.9 * self.system_load + 0.1 * latency_load
    
    def _update_strategy_performance(
        self, 
        strategy: OrchestrationStrategy,
        response_time: float,
        quality_score: float,
        cost: float,
        success: bool
    ) -> None:
        """
        Update performance metrics for a strategy.
        
        Args:
            strategy: The strategy used
            response_time: Time taken to process the request
            quality_score: Subjective quality score of the response (0.0-1.0)
            cost: Estimated cost of the request
            success: Whether the request was successful
        """
        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = {
                "avg_response_time": response_time,
                "avg_quality": quality_score,
                "avg_cost": cost,
                "success_rate": 1.0 if success else 0.0,
                "count": 1
            }
            return
            
        # Update with exponential moving average
        perf = self.strategy_performance[strategy]
        count = perf["count"]
        alpha = self.learning_rate  # Weight for the new sample
        
        perf["avg_response_time"] = (1 - alpha) * perf["avg_response_time"] + alpha * response_time
        perf["avg_quality"] = (1 - alpha) * perf["avg_quality"] + alpha * quality_score
        perf["avg_cost"] = (1 - alpha) * perf["avg_cost"] + alpha * cost
        perf["success_rate"] = (1 - alpha) * perf["success_rate"] + alpha * (1.0 if success else 0.0)
        perf["count"] += 1
    
    def _select_strategy(self, prompt: str, **options) -> OrchestrationStrategy:
        """
        Select the best strategy for the current request context.
        
        Args:
            prompt: The prompt to process
            **options: Additional request options
            
        Returns:
            The selected orchestration strategy
        """
        # If strategy explicitly specified in options, use it
        if "strategy" in options:
            strategy_name = options.pop("strategy")
            try:
                return OrchestrationStrategy(strategy_name)
            except ValueError:
                self.logger.warning(f"Invalid strategy '{strategy_name}', using default")
                return self.default_strategy
        
        # If using ADAPTIVE, select the best strategy for the context
        if self.default_strategy == OrchestrationStrategy.ADAPTIVE:
            # If under high system load, prioritize efficiency
            if self.system_load > 0.8:
                return OrchestrationStrategy.COST_OPTIMIZED
                
            # If prioritization specified in options
            if "prioritize" in options:
                priority = options.pop("prioritize").lower()
                if priority == "quality":
                    return OrchestrationStrategy.QUALITY_OPTIMIZED
                elif priority == "speed":
                    return OrchestrationStrategy.SPEED_OPTIMIZED
                elif priority == "cost":
                    return OrchestrationStrategy.COST_OPTIMIZED
            
            # Analyze prompt characteristics to choose strategy
            # (simplified heuristic - production system would use more sophisticated analysis)
            prompt_length = len(prompt)
            
            # For short prompts, optimize for speed
            if prompt_length < 200:
                return OrchestrationStrategy.SPEED_OPTIMIZED
                
            # For very long prompts, optimize for quality
            if prompt_length > 1000:
                return OrchestrationStrategy.QUALITY_OPTIMIZED
                
            # For medium length prompts, use balanced approach
            return OrchestrationStrategy.BALANCED
            
        # Otherwise use the default strategy
        return self.default_strategy
    
    def _estimate_request_cost(self, provider_id: str, prompt: str) -> float:
        """
        Estimate the cost of a request to a provider.
        
        Args:
            provider_id: The provider ID
            prompt: The prompt text
            
        Returns:
            Estimated cost in units (abstract cost units)
        """
        # Get provider config
        if provider_id not in self.provider_configs:
            return 1.0  # Default cost unit
            
        config = self.provider_configs[provider_id]
        provider_type = config.get("provider_type", "unknown")
        model = config.get("model", "unknown")
        
        # Get prompt length in tokens (simplified estimate)
        token_count = len(prompt.split())
        
        # Base costs per provider (highly simplified - production would use real pricing)
        base_costs = {
            "openai": 0.5,
            "anthropic": 0.7,
            "google": 0.3,
            "cohere": 0.2,
            "mistral": 0.1,
            "mock": 0.0
        }
        
        # Get base cost for this provider
        base_cost = base_costs.get(provider_type, 0.5)
        
        # Adjust cost based on model (simplified - production would use model-specific pricing)
        model_factors = {
            "gpt-4": 2.0,
            "claude-3-opus": 2.0,
            "claude-3-sonnet": 1.5,
            "claude-3-haiku": 0.8,
            "gemini-1.5-pro": 1.5,
            "gemini-1.5-flash": 0.8,
            "command-r": 1.0,
            "mistral-large": 1.0,
            "mistral-medium": 0.5,
            "mistral-small": 0.3
        }
        
        # Get model factor
        model_factor = 1.0
        for model_name, factor in model_factors.items():
            if model_name in model:
                model_factor = factor
                break
        
        # Calculate final cost estimate
        # Cost = base_cost * model_factor * (token_count/1000)
        return base_cost * model_factor * (token_count / 1000)
    
    def _select_providers(
        self, 
        strategy: OrchestrationStrategy,
        provider_ids: List[str],
        prompt: str
    ) -> List[str]:
        """
        Select the best providers for the current strategy and context.
        
        Args:
            strategy: The orchestration strategy
            provider_ids: Available provider IDs
            prompt: The prompt to process
            
        Returns:
            List of selected provider IDs
        """
        if not provider_ids:
            return []
            
        # Calculate scores for all providers
        scores: Dict[str, float] = {}
        
        for pid in provider_ids:
            # Get provider stats
            stats = self.request_stats.get(pid, {})
            success_rate = (
                stats.get("requests_successful", 0) / stats.get("requests_total", 1)
                if stats.get("requests_total", 0) > 0 else 0.5
            )
            
            avg_latency = (
                stats.get("total_latency", 0) / stats.get("requests_successful", 1)
                if stats.get("requests_successful", 0) > 0 else self.timeout_seconds
            )
            
            # Normalize latency (0-1, where 1 is fastest)
            norm_latency = 1.0 - min(1.0, avg_latency / self.timeout_seconds)
            
            # Estimate cost
            cost = self._estimate_request_cost(pid, prompt)
            norm_cost = 1.0 - min(1.0, cost / 2.0)  # Normalize cost (0-1, where 1 is cheapest)
            
            # Calculate composite score based on strategy
            if strategy == OrchestrationStrategy.QUALITY_OPTIMIZED:
                # Prioritize success rate (reliability)
                scores[pid] = (0.7 * success_rate) + (0.2 * norm_latency) + (0.1 * norm_cost)
                
            elif strategy == OrchestrationStrategy.SPEED_OPTIMIZED:
                # Prioritize latency (speed)
                scores[pid] = (0.2 * success_rate) + (0.7 * norm_latency) + (0.1 * norm_cost)
                
            elif strategy == OrchestrationStrategy.COST_OPTIMIZED:
                # Prioritize cost
                scores[pid] = (0.2 * success_rate) + (0.1 * norm_latency) + (0.7 * norm_cost)
                
            elif strategy in (OrchestrationStrategy.BALANCED, OrchestrationStrategy.ADAPTIVE):
                # Balanced approach
                scores[pid] = (0.4 * success_rate) + (0.3 * norm_latency) + (0.3 * norm_cost)
                
            else:
                # Default balanced scoring
                scores[pid] = (0.33 * success_rate) + (0.33 * norm_latency) + (0.33 * norm_cost)
        
        # Sort providers by score
        sorted_providers = sorted(provider_ids, key=lambda pid: scores.get(pid, 0), reverse=True)
        
        # Limit by max_providers_per_request, except for quality optimized
        if strategy == OrchestrationStrategy.QUALITY_OPTIMIZED:
            # Use all providers for quality-optimized approach
            return sorted_providers
        else:
            return sorted_providers[:self.max_providers_per_request]
    
    async def _strategy_simple(
        self, 
        prompt: str, 
        provider_ids: List[str],
        **options
    ) -> Dict[str, Any]:
        """
        Implement the SIMPLE strategy using the SimpleOrchestrator.
        
        Args:
            prompt: The prompt to process
            provider_ids: Available provider IDs
            **options: Additional processing options
            
        Returns:
            Processing results
        """
        # Select appropriate providers for this strategy
        selected_providers = self._select_providers(
            OrchestrationStrategy.SIMPLE, provider_ids, prompt
        )
        
        # Use the SimpleOrchestrator
        simple_orchestrator = self._get_simple_orchestrator()
        return await simple_orchestrator.process(prompt, selected_providers, **options)
    
    async def _strategy_parallel(
        self, 
        prompt: str, 
        provider_ids: List[str],
        **options
    ) -> Dict[str, Any]:
        """
        Implement the PARALLEL strategy using the ParallelOrchestrator.
        
        Args:
            prompt: The prompt to process
            provider_ids: Available provider IDs
            **options: Additional processing options
            
        Returns:
            Processing results
        """
        # Select appropriate providers for this strategy
        selected_providers = self._select_providers(
            OrchestrationStrategy.PARALLEL, provider_ids, prompt
        )
        
        # Use the ParallelOrchestrator
        parallel_orchestrator = self._get_parallel_orchestrator()
        
        # Configure early stopping based on options
        use_early_stopping = options.pop("use_early_stopping", True)
        min_responses = options.pop("min_responses", 1)
        
        parallel_orchestrator.use_early_stopping = use_early_stopping
        parallel_orchestrator.min_responses_needed = min_responses
        
        return await parallel_orchestrator.process(prompt, selected_providers, **options)
    
    async def _strategy_waterfall(
        self, 
        prompt: str, 
        provider_ids: List[str],
        **options
    ) -> Dict[str, Any]:
        """
        Implement the WATERFALL strategy using fallback_chain.
        
        Args:
            prompt: The prompt to process
            provider_ids: Available provider IDs
            **options: Additional processing options
            
        Returns:
            Processing results
        """
        # Select and order providers for the waterfall
        selected_providers = self._select_providers(
            OrchestrationStrategy.WATERFALL, provider_ids, prompt
        )
        
        start_time = asyncio.get_event_loop().time()
        
        # Try providers in sequence until one succeeds
        result = await self.fallback_chain(prompt, selected_providers, **options)
        
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        if not result:
            # All providers failed
            return {
                "error": "All providers in waterfall sequence failed",
                "responses": [
                    {
                        "provider_id": pid,
                        "success": False,
                        "error": "Failed in waterfall sequence",
                    }
                    for pid in selected_providers
                ],
                "best_response": None,
                "metadata": {
                    "processing_time": processing_time,
                    "providers_requested": len(selected_providers),
                    "providers_successful": 0,
                    "strategy": OrchestrationStrategy.WATERFALL.value
                }
            }
        
        # Format successful response
        response, metadata = result
        successful_provider = metadata.get("provider_id", selected_providers[0])
        
        return {
            "responses": [
                {
                    "provider_id": pid,
                    "success": pid == successful_provider,
                    "response": response if pid == successful_provider else None,
                    "metadata": metadata if pid == successful_provider else None,
                    "error": "Not attempted (previous provider succeeded)" if pid != successful_provider else None
                }
                for pid in selected_providers
            ],
            "best_response": {
                "provider_id": successful_provider,
                "response": response,
                "metadata": metadata
            },
            "metadata": {
                "processing_time": processing_time,
                "providers_requested": len(selected_providers),
                "providers_successful": 1,
                "strategy": OrchestrationStrategy.WATERFALL.value,
                "successful_provider": successful_provider
            }
        }
    
    async def _strategy_balanced(
        self, 
        prompt: str, 
        provider_ids: List[str],
        **options
    ) -> Dict[str, Any]:
        """
        Implement the BALANCED strategy (compromise between quality and efficiency).
        
        Args:
            prompt: The prompt to process
            provider_ids: Available provider IDs
            **options: Additional processing options
            
        Returns:
            Processing results
        """
        # For balanced approach, use parallel with early stopping and 2 min responses
        selected_providers = self._select_providers(
            OrchestrationStrategy.BALANCED, provider_ids, prompt
        )
        
        # Use parallel orchestrator with custom settings
        parallel_orchestrator = self._get_parallel_orchestrator()
        parallel_orchestrator.use_early_stopping = True
        parallel_orchestrator.min_responses_needed = 2
        
        result = await parallel_orchestrator.process(prompt, selected_providers, **options)
        
        # Add strategy info to metadata
        if "metadata" in result:
            result["metadata"]["strategy"] = OrchestrationStrategy.BALANCED.value
            
        return result
    
    async def _strategy_cost_optimized(
        self, 
        prompt: str, 
        provider_ids: List[str],
        **options
    ) -> Dict[str, Any]:
        """
        Implement the COST_OPTIMIZED strategy.
        
        Args:
            prompt: The prompt to process
            provider_ids: Available provider IDs
            **options: Additional processing options
            
        Returns:
            Processing results
        """
        # For cost optimization, try cheaper providers first with waterfall approach
        sorted_by_cost = sorted(
            provider_ids,
            key=lambda pid: self._estimate_request_cost(pid, prompt)
        )
        
        # Take the 2-3 cheapest options
        selected_providers = sorted_by_cost[:min(3, len(sorted_by_cost))]
        
        # Use waterfall approach
        return await self._strategy_waterfall(prompt, selected_providers, **options)
    
    async def _strategy_quality_optimized(
        self, 
        prompt: str, 
        provider_ids: List[str],
        **options
    ) -> Dict[str, Any]:
        """
        Implement the QUALITY_OPTIMIZED strategy.
        
        Args:
            prompt: The prompt to process
            provider_ids: Available provider IDs
            **options: Additional processing options
            
        Returns:
            Processing results
        """
        # For quality optimization, use simple orchestrator with all providers
        # This gets responses from all providers and does analysis + synthesis
        selected_providers = self._select_providers(
            OrchestrationStrategy.QUALITY_OPTIMIZED, provider_ids, prompt
        )
        
        # Use SimpleOrchestrator for full analysis workflow
        simple_orchestrator = self._get_simple_orchestrator()
        
        # Set analysis type to comparative for quality focus
        original_analysis_type = getattr(simple_orchestrator, "analysis_type", "comparative")
        simple_orchestrator.analysis_type = "comparative"
        
        result = await simple_orchestrator.process(prompt, selected_providers, **options)
        
        # Restore original analysis type
        simple_orchestrator.analysis_type = original_analysis_type
        
        # Add strategy info to metadata
        if "metadata" in result:
            result["metadata"]["strategy"] = OrchestrationStrategy.QUALITY_OPTIMIZED.value
            
        return result
    
    async def _strategy_speed_optimized(
        self, 
        prompt: str, 
        provider_ids: List[str],
        **options
    ) -> Dict[str, Any]:
        """
        Implement the SPEED_OPTIMIZED strategy.
        
        Args:
            prompt: The prompt to process
            provider_ids: Available provider IDs
            **options: Additional processing options
            
        Returns:
            Processing results
        """
        # For speed optimization, use parallel with aggressive early stopping
        selected_providers = self._select_providers(
            OrchestrationStrategy.SPEED_OPTIMIZED, provider_ids, prompt
        )
        
        # Use parallel orchestrator with speed-focused settings
        parallel_orchestrator = self._get_parallel_orchestrator()
        parallel_orchestrator.use_early_stopping = True
        parallel_orchestrator.min_responses_needed = 1
        
        result = await parallel_orchestrator.process(prompt, selected_providers, **options)
        
        # Add strategy info to metadata
        if "metadata" in result:
            result["metadata"]["strategy"] = OrchestrationStrategy.SPEED_OPTIMIZED.value
            
        return result
    
    async def _strategy_adaptive(
        self, 
        prompt: str, 
        provider_ids: List[str],
        **options
    ) -> Dict[str, Any]:
        """
        Implement the ADAPTIVE strategy (select best strategy for context).
        
        Args:
            prompt: The prompt to process
            provider_ids: Available provider IDs
            **options: Additional processing options
            
        Returns:
            Processing results
        """
        # This is a meta-strategy that selects another strategy based on context
        # Since _select_strategy already handles the logic when ADAPTIVE is passed,
        # and we don't want infinite recursion, we'll default to BALANCED here
        return await self._strategy_balanced(prompt, provider_ids, **options)
    
    async def process(
        self, 
        prompt: str,
        provider_ids: Optional[List[str]] = None,
        **options
    ) -> Dict[str, Any]:
        """
        Process a prompt using the adaptive orchestration system.
        
        Args:
            prompt: The prompt to process
            provider_ids: Optional list of provider IDs to use (defaults to all registered)
            **options: Additional processing options
            
        Returns:
            Dictionary with processing results
        """
        start_time = asyncio.get_event_loop().time()
        
        # Get provider IDs to use
        if provider_ids is None:
            provider_ids = list(self.providers.keys())
            
        # Validate provider IDs
        valid_provider_ids = [pid for pid in provider_ids if pid in self.providers]
        
        if not valid_provider_ids:
            error_msg = "No valid providers specified"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "strategy": self.default_strategy.value,
                "responses": [],
                "metadata": {
                    "processing_time": 0,
                    "providers_requested": len(provider_ids) if provider_ids else 0,
                    "providers_successful": 0
                }
            }
        
        # Select the best strategy for this request
        strategy = self._select_strategy(prompt, **options.copy())
        self.logger.info(f"Selected strategy: {strategy.value}")
        
        # Execute the selected strategy
        strategy_handler = self.strategy_handlers.get(strategy)
        if not strategy_handler:
            self.logger.error(f"No handler for strategy {strategy.value}")
            strategy = OrchestrationStrategy.BALANCED
            strategy_handler = self.strategy_handlers.get(strategy)
        
        # Process using the selected strategy
        result = await strategy_handler(prompt, valid_provider_ids, **options)
        
        # Calculate processing time
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        # Update system state
        self._update_system_state(processing_time)
        
        # Update strategy performance
        quality_score = 0.8  # Placeholder - would be calculated from actual response quality
        cost = sum(
            self._estimate_request_cost(pid, prompt)
            for pid in valid_provider_ids
        )
        success = "error" not in result
        
        self._update_strategy_performance(
            strategy, processing_time, quality_score, cost, success
        )
        
        # Add strategy info to result
        if isinstance(result, dict) and "metadata" in result:
            result["metadata"]["strategy"] = strategy.value
        
        return result
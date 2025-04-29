"""
Enhanced Orchestrator Module.

This module provides an improved orchestration system for managing multiple LLMs,
applying analysis patterns, tracking progress, and implementing circuit breakers
for fault tolerance.
"""

import asyncio
import json
import logging
import time
import hashlib
from dataclasses import dataclass, field
from string import Template
from typing import Any, Callable, Dict, List, Optional, AsyncGenerator

from src.models.circuit_breaker import CircuitBreakerRegistry
from src.models.llm_adapter import LLMAdapter, create_adapter
from src.models.progress_tracker import ProgressStatus, ProgressTracker, ProgressUpdate
from src.patterns.ultra_analysis_patterns import get_pattern_mapping
from src.models import ModelResponse, QualityMetrics, ResponseCache
from src.models.resource_optimizer import ResourceOptimizer, OptimizationAction


@dataclass
class AnalysisMode:
    """
    Configuration for an analysis mode.

    Attributes:
        name: Name of the analysis mode
        pattern: The analysis pattern to use
        models: Models to include or None for all available
        model_selection_strategy: How to select models if multiple are available
        evaluate_quality: Whether to evaluate response quality
        cache_responses: Whether to cache responses
        timeout: Maximum time to wait for responses (None = wait indefinitely)
    """

    name: str
    pattern: str
    models: Optional[List[str]] = None
    model_selection_strategy: str = "weighted"  # weighted, all, best, random
    evaluate_quality: bool = True
    cache_responses: bool = True
    timeout: Optional[float] = None

    def __post_init__(self):
        """Validate attributes."""
        valid_strategies = ["weighted", "all", "best", "random"]
        if self.model_selection_strategy not in valid_strategies:
            raise ValueError(
                f"Invalid model selection strategy: {self.model_selection_strategy}. "
                f"Valid strategies are: {valid_strategies}"
            )


@dataclass
class OrchestratorConfig:
    """
    Configuration for the enhanced orchestrator.

    Attributes:
        cache_enabled: Whether to use caching for responses
        max_retries: Maximum number of retries for failed requests
        retry_base_delay: Base delay in seconds for retry backoff
        parallel_processing: Whether to use parallel processing
        max_workers: Maximum number of worker threads (None = auto)
        circuit_breaker_enabled: Whether to use circuit breakers
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before testing service
        default_pattern: Default analysis pattern to use
        default_output_format: Default output format
        collect_metrics: Whether to collect performance metrics
        analysis_modes: Predefined analysis modes
    """

    cache_enabled: bool = True
    max_retries: int = 3
    retry_base_delay: float = 0.5
    parallel_processing: bool = True
    max_workers: Optional[int] = None
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout: int = 60
    default_pattern: str = "gut"
    default_output_format: str = "plain"
    collect_metrics: bool = True
    analysis_modes: Dict[str, AnalysisMode] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize with default analysis modes if none provided."""
        if not self.analysis_modes:
            self.analysis_modes = {
                "standard": AnalysisMode(
                    name="standard",
                    pattern=self.default_pattern,
                    evaluate_quality=self.collect_metrics,
                    cache_responses=self.cache_enabled,
                ),
                "fast": AnalysisMode(
                    name="fast",
                    pattern="gut",
                    model_selection_strategy="best",
                    evaluate_quality=False,
                    cache_responses=True,
                    timeout=30.0,
                ),
                "thorough": AnalysisMode(
                    name="thorough",
                    pattern="confidence",
                    model_selection_strategy="all",
                    evaluate_quality=True,
                    cache_responses=True,
                ),
                "creative": AnalysisMode(
                    name="creative",
                    pattern="perspective",
                    model_selection_strategy="all",
                    evaluate_quality=True,
                    cache_responses=True,
                ),
            }


@dataclass
class ModelRegistration:
    """
    Registration information for an LLM.

    Attributes:
        adapter: The LLM adapter instance
        provider: The provider name (openai, anthropic, etc.)
        model: The specific model name
        weight: The weight for prioritizing model responses
        capabilities: Dictionary of model capabilities
        tags: Optional tags for model categorization
    """

    adapter: LLMAdapter
    provider: str
    model: str
    weight: float = 1.0
    capabilities: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class EnhancedOrchestrator:
    """
    Enhanced orchestrator for multiple LLMs with pattern support, progress tracking,
    and circuit breakers.

    Features:
    - Standardized LLM integration through adapters
    - Analysis pattern application
    - Progress tracking and reporting
    - Circuit breaker for fault tolerance
    - Efficient parallel processing
    - Streaming response support
    - Resource optimization and monitoring
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """
        Initialize the enhanced orchestrator.

        Args:
            config: Optional orchestrator configuration
        """
        self.config = config or OrchestratorConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize adapters registry
        self.model_registry: Dict[str, ModelRegistration] = {}

        # Initialize analysis patterns
        self.patterns = get_pattern_mapping()

        # Initialize circuit breakers
        self.circuit_breakers = CircuitBreakerRegistry()

        # Initialize response cache
        self.cache = ResponseCache() if self.config.cache_enabled else None

        # Initialize metrics
        self.metrics = {
            "response_times": [],
            "success_rates": {},
            "token_usage": {},
            "quality_scores": {},
        }

        # Initialize resource optimizer
        self.resource_optimizer = ResourceOptimizer(
            enable_adaptive_concurrency=True,
            enable_gc_optimization=True,
            monitoring_interval_seconds=30.0,
        )

        # Register action callbacks for resource optimization
        self._register_optimization_callbacks()

        self.logger.info(
            f"Initialized EnhancedOrchestrator with config: {self.config.__dict__}"
        )

    def _register_optimization_callbacks(self) -> None:
        """Register callbacks for optimization actions."""
        # When CLEAR_CACHE action is triggered, clear the response cache
        self.resource_optimizer.add_action_callback(
            OptimizationAction.CLEAR_CACHE,
            lambda: self.clear_cache() if self.cache else None,
        )

        # When REDUCE_CONCURRENCY action is triggered, adjust max_workers
        self.resource_optimizer.add_action_callback(
            OptimizationAction.REDUCE_CONCURRENCY,
            lambda: setattr(
                self.config,
                "max_workers",
                max(1, self.config.max_workers - 1) if self.config.max_workers else 2,
            ),
        )

        # When INCREASE_CONCURRENCY action is triggered, adjust max_workers
        self.resource_optimizer.add_action_callback(
            OptimizationAction.INCREASE_CONCURRENCY,
            lambda: setattr(
                self.config,
                "max_workers",
                (self.config.max_workers + 1) if self.config.max_workers else 4,
            ),
        )

    def register_model(
        self,
        name: str,
        api_key: str,
        provider: str,
        model: Optional[str] = None,
        weight: float = 1.0,
        tags: Optional[List[str]] = None,
    ):
        """
        Register a new model by creating an appropriate adapter.

        Args:
            name: Unique identifier for the model
            api_key: API key for the provider
            provider: LLM provider (openai, anthropic, etc.)
            model: Specific model name (optional)
            weight: Weight for prioritizing model responses
            tags: Optional tags for model categorization
        """
        adapter = create_adapter(provider, api_key, model=model)
        capabilities = adapter.get_capabilities()

        self.model_registry[name] = ModelRegistration(
            adapter=adapter,
            provider=provider,
            model=model or capabilities.get("name", provider),
            weight=weight,
            capabilities=capabilities,
            tags=tags or [],
        )

        self.logger.info(
            f"Registered model '{name}' ({provider}/{model}) with weight {weight}"
        )

    def get_model_by_tag(self, tag: str) -> List[str]:
        """
        Get models that have a specific tag.

        Args:
            tag: The tag to search for

        Returns:
            List of model names with the specified tag
        """
        return [
            name
            for name, registration in self.model_registry.items()
            if tag in registration.tags
        ]

    def get_models_by_capability(self, capability: str, value: Any = True) -> List[str]:
        """
        Get models that have a specific capability.

        Args:
            capability: The capability to search for
            value: The expected value of the capability

        Returns:
            List of model names with the specified capability
        """
        return [
            name
            for name, registration in self.model_registry.items()
            if registration.capabilities.get(capability) == value
        ]

    def set_model_weight(self, name: str, weight: float):
        """
        Set or update the weight for a registered model.

        Args:
            name: The name of the registered model
            weight: New weight value (higher = more important)

        Raises:
            ValueError: If the model is not registered
        """
        if name not in self.model_registry:
            raise ValueError(f"Model '{name}' is not registered")

        self.model_registry[name].weight = weight
        self.logger.info(f"Updated weight for model '{name}' to {weight}")

    def get_prioritized_models(
        self, required_models: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get a list of model names sorted by their weights (highest first).

        Args:
            required_models: Optional list of specific models to include

        Returns:
            List of model names sorted by weight
        """
        if required_models:
            model_subset = {
                k: v.weight
                for k, v in self.model_registry.items()
                if k in required_models
            }
        else:
            model_subset = {k: v.weight for k, v in self.model_registry.items()}

        return sorted(model_subset.keys(), key=lambda m: model_subset[m], reverse=True)

    async def evaluate_quality(self, response: ModelResponse) -> QualityMetrics:
        """
        Evaluate response quality using a reference model.

        Args:
            response: The model response to evaluate

        Returns:
            Quality metrics for the response
        """
        # Use first available model for evaluation, preferably OpenAI
        eval_models = [
            m
            for m, reg in self.model_registry.items()
            if "gpt" in m.lower() or reg.provider.lower() == "openai"
        ]
        if not eval_models and self.model_registry:
            eval_models = [next(iter(self.model_registry.keys()))]

        if not eval_models:
            self.logger.warning("No models available for quality evaluation")
            return QualityMetrics()

        eval_model_name = eval_models[0]
        eval_adapter = self.model_registry[eval_model_name].adapter

        try:
            prompt_template = Template(
                "Evaluate the quality of this LLM response. Consider coherence, "
                "technical depth, relevance, readability, and overall quality. "
                'Return scores in JSON format like: {"coherence": 0.8, '
                '"technical_depth": 0.7, "relevance": 0.9, "readability": 0.8, '
                '"overall": 0.85}.'
                "\n\nPrompt: $original_prompt\n\nResponse: $response"
            )
            eval_prompt = prompt_template.safe_substitute(
                original_prompt=response.prompt, response=response.content
            )

            # Check circuit breaker
            if self.config.circuit_breaker_enabled:
                circuit = self.circuit_breakers.get_or_create(
                    f"quality_eval_{eval_model_name}",
                    failure_threshold=self.config.failure_threshold,
                    recovery_timeout=self.config.recovery_timeout,
                )

                if not circuit.allow_request():
                    self.logger.warning(
                        f"Circuit open for {eval_model_name}, "
                        f"skipping quality evaluation"
                    )
                    return QualityMetrics()

            eval_response = await eval_adapter.generate(eval_prompt)

            # Record circuit breaker success
            if self.config.circuit_breaker_enabled:
                circuit.record_success()

            # Parse JSON response
            try:
                scores = json.loads(eval_response)
                return QualityMetrics(
                    coherence_score=scores.get("coherence", 0.0),
                    technical_depth=scores.get("technical_depth", 0.0),
                    strategic_value=scores.get("strategic_value", 0.0),
                    uniqueness=scores.get("uniqueness", 0.0),
                )
            except json.JSONDecodeError:
                self.logger.error(
                    f"Failed to parse quality evaluation: {eval_response}"
                )
                return QualityMetrics()

        except Exception as e:
            self.logger.error(f"Quality evaluation failed: {e}")

            # Record circuit breaker failure
            if self.config.circuit_breaker_enabled:
                circuit.record_failure()

            return QualityMetrics()

    async def get_model_response(
        self,
        model_name: str,
        prompt: str,
        stage: str,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
    ) -> ModelResponse:
        """
        Get a response from a specific model with caching and retry support.

        Args:
            model_name: The name of the model to use
            prompt: The prompt to process
            stage: The processing stage (for caching and progress)
            use_cache: Whether to use caching
            progress_callback: Optional callback for progress updates

        Returns:
            ModelResponse with content and metadata

        Raises:
            ValueError: If the model is not registered
            RuntimeError: If the request fails after retries
        """
        if model_name not in self.model_registry:
            raise ValueError(f"Model '{model_name}' not registered")

        # Check cache first
        cache_key = f"{model_name}:{stage}:{hash(prompt)}"
        if use_cache and self.cache and self.config.cache_enabled:
            cached_response = self.cache.get(cache_key)
            if cached_response:
                self.logger.info(f"Cache hit for {model_name} in stage {stage}")
                if progress_callback:
                    progress_callback(
                        ProgressUpdate(
                            model=model_name,
                            stage=stage,
                            status=ProgressStatus.COMPLETED,
                            message="Retrieved from cache",
                        )
                    )
                return cached_response

        # Get the model registration
        model_reg = self.model_registry[model_name]
        adapter = model_reg.adapter

        # Check circuit breaker
        if self.config.circuit_breaker_enabled:
            circuit = self.circuit_breakers.get_or_create(
                model_name,
                failure_threshold=self.config.failure_threshold,
                recovery_timeout=self.config.recovery_timeout,
            )

            if not circuit.allow_request():
                self.logger.warning(f"Circuit open for {model_name}, skipping request")
                raise RuntimeError(f"Circuit breaker open for {model_name}")

        # Update progress
        if progress_callback:
            progress_callback(
                ProgressUpdate(
                    model=model_name,
                    stage=stage,
                    status=ProgressStatus.STARTED,
                    message="Starting request",
                )
            )

        # Initialize retry count
        retry_count = 0
        max_retries = self.config.max_retries
        last_error = None

        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    self.logger.warning(
                        f"Retrying {model_name} request ({retry_count}/{max_retries})"
                    )
                    if progress_callback:
                        progress_callback(
                            ProgressUpdate(
                                model=model_name,
                                stage=stage,
                                status=ProgressStatus.RETRYING,
                                message=f"Retrying ({retry_count}/{max_retries})",
                            )
                        )

                # Record start time for metrics
                start_time = time.time()

                # Get response from model
                content = await adapter.generate(prompt)

                # Record request duration
                response_time = time.time() - start_time

                # Create response object
                response = ModelResponse(
                    model=model_name,
                    content=content,
                    prompt=prompt,
                    timestamp=time.time(),
                    tokens_used=len(content.split()) // 4,  # Rough estimate
                    quality=(
                        await self.evaluate_quality(
                            ModelResponse(
                                model=model_name,
                                content=content,
                                prompt=prompt,
                                timestamp=time.time(),
                            )
                        )
                        if self.config.collect_metrics
                        else QualityMetrics()
                    ),
                )

                # Update metrics
                self._update_metrics(response, response_time)

                # Record circuit breaker success
                if self.config.circuit_breaker_enabled:
                    circuit.record_success()

                # Update progress
                if progress_callback:
                    progress_callback(
                        ProgressUpdate(
                            model=model_name,
                            stage=stage,
                            status=ProgressStatus.COMPLETED,
                            message="Request completed",
                        )
                    )

                # Cache the response
                if self.cache and self.config.cache_enabled:
                    self.cache.set(cache_key, response)

                return response

            except Exception as e:
                last_error = e
                self.logger.error(f"Error getting response from {model_name}: {e}")
                retry_count += 1

                # Record circuit breaker failure
                if self.config.circuit_breaker_enabled:
                    circuit.record_failure()

                # Update progress
                if progress_callback:
                    progress_callback(
                        ProgressUpdate(
                            model=model_name,
                            stage=stage,
                            status=ProgressStatus.ERROR,
                            message=f"Error: {str(e)}",
                        )
                    )

                # Wait before retrying (exponential backoff)
                if retry_count <= max_retries:
                    await asyncio.sleep(2**retry_count)

        # If we've exhausted all retries
        error_msg = (
            f"Failed to get response from {model_name} after {max_retries} retries"
        )
        self.logger.error(error_msg)
        raise RuntimeError(error_msg) from last_error

    def _update_metrics(self, response: ModelResponse, response_time: float):
        """
        Update metrics with a new response.

        Args:
            response: The model response
            response_time: The time taken to receive the response
        """
        if not self.config.collect_metrics:
            return

        # Update response times
        self.metrics["response_times"].append(response_time)

        # Update success rates
        model = response.model
        if model not in self.metrics["success_rates"]:
            self.metrics["success_rates"][model] = {"total": 0, "success": 0}
        self.metrics["success_rates"][model]["total"] += 1
        self.metrics["success_rates"][model]["success"] += 1

        # Update token usage
        if model not in self.metrics["token_usage"]:
            self.metrics["token_usage"][model] = 0
        self.metrics["token_usage"][model] += response.tokens_used

        # Update quality scores
        if response.quality:
            if model not in self.metrics["quality_scores"]:
                self.metrics["quality_scores"][model] = []
            # Use average of all quality metrics
            avg_quality = (
                sum(
                    [
                        response.quality.coherence_score,
                        response.quality.technical_depth,
                        response.quality.strategic_value,
                        response.quality.uniqueness,
                    ]
                )
                / 4
            )
            self.metrics["quality_scores"][model].append(avg_quality)

    def _create_stage_prompt(
        self, stage: str, context: Dict[str, Any], pattern_name: str
    ) -> str:
        """
        Create a prompt for a specific stage using templates.

        Args:
            stage: The processing stage
            context: Context with variables for the template
            pattern_name: The analysis pattern to use

        Returns:
            Formatted prompt for the stage
        """
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            self.logger.error(f"Unknown pattern: {pattern_name}")
            return context.get("original_prompt", "")

        # Get template for this stage
        template_str = pattern.templates.get(stage)
        if not template_str:
            self.logger.error(
                f"No template for stage {stage} in pattern {pattern_name}"
            )
            return context.get("original_prompt", "")

        # Apply template with context variables
        try:
            template = Template(template_str)
            return template.safe_substitute(**context)
        except KeyError as e:
            self.logger.error(f"Missing context variable for template: {e}")
            return context.get("original_prompt", "")
        except Exception as e:
            self.logger.error(f"Error applying template: {e}")
            return context.get("original_prompt", "")

    async def _process_stage(
        self,
        stage: str,
        models: List[str],
        context: Dict[str, Any],
        pattern_name: str,
        progress_tracker: ProgressTracker,
    ) -> Dict[str, ModelResponse]:
        """
        Process a single stage with multiple models.

        Args:
            stage: The processing stage
            models: List of models to use
            context: Context with variables for the template
            pattern_name: The analysis pattern to use
            progress_tracker: Progress tracker instance

        Returns:
            Dictionary mapping model names to responses
        """
        # Create stage-specific prompt from template
        prompt = self._create_stage_prompt(stage, context, pattern_name)

        # Create tasks for all models
        tasks = []
        for model_name in models:
            # Create progress update callback
            def make_callback(model):
                def callback(update: ProgressUpdate):
                    # Update progress tracker
                    progress_tracker.update(
                        model=update.model,
                        stage=update.stage,
                        status=update.status,
                        message=update.message,
                    )

                return callback

            # Add task to get model response
            task = self.get_model_response(
                model_name=model_name,
                prompt=prompt,
                stage=stage,
                progress_callback=make_callback(model_name),
            )
            tasks.append((model_name, task))

        # Execute all tasks
        responses = {}
        for model_name, task in tasks:
            try:
                response = await task
                responses[model_name] = response
            except Exception as e:
                self.logger.error(f"Error in {model_name} for stage {stage}: {e}")
                # Update progress tracker with error
                progress_tracker.update(
                    model=model_name,
                    stage=stage,
                    status=ProgressStatus.ERROR,
                    message=f"Error: {str(e)}",
                )

        return responses

    async def process_in_parallel(
        self,
        prompts: List[str],
        model_names: Optional[List[str]] = None,
        stage: str = "batch",
        batch_size: int = 3,
        max_concurrent_batches: int = 2,
        timeout: Optional[float] = None,
    ) -> List[ModelResponse]:
        """
        Process multiple prompts in parallel with batching and concurrency control.

        Args:
            prompts: List of prompts to process
            model_names: List of model names to use (default: all registered models)
            stage: Processing stage name
            batch_size: Number of prompts to process in each batch
            max_concurrent_batches: Maximum number of batches to process concurrently
            timeout: Maximum time to wait for responses (None = wait indefinitely)

        Returns:
            List of model responses
        """
        # Check and optimize resources before processing
        resource_status = self.resource_optimizer.get_resource_status()

        # Adjust batch size and concurrency based on resource availability
        if (
            resource_status.get("memory") == "critical"
            or resource_status.get("cpu") == "critical"
        ):
            self.logger.warning(
                "Resource constraints detected, reducing batch size and concurrency"
            )
            batch_size = max(1, batch_size - 1)
            max_concurrent_batches = max(1, max_concurrent_batches - 1)

        if model_names is None:
            model_names = list(self.model_registry.keys())

        invalid_models = [m for m in model_names if m not in self.model_registry]
        if invalid_models:
            raise ValueError(f"Invalid model(s) specified: {invalid_models}")

        # Create all tasks
        all_tasks = []
        for model_name in model_names:
            for prompt in prompts:
                all_tasks.append((model_name, prompt))

        # Split into batches
        batches = [
            all_tasks[i:i + batch_size] for i in range(0, len(all_tasks), batch_size)
        ]
        results = []

        # Use resource optimizer's adaptive concurrency
        actual_concurrent_batches = (
            self.resource_optimizer.concurrency_config.current_concurrency
        )
        if actual_concurrent_batches != max_concurrent_batches:
            self.logger.info(
                f"Using resource optimizer's concurrency: {actual_concurrent_batches}"
            )
            max_concurrent_batches = actual_concurrent_batches

        # Process batches with concurrency control
        for i in range(0, len(batches), max_concurrent_batches):
            current_batches = batches[i:i + max_concurrent_batches]
            batch_tasks = []

            for batch in current_batches:
                batch_futures = []
                for model_name, prompt in batch:
                    task = self.get_model_response(
                        model_name=model_name,
                        prompt=prompt,
                        stage=stage,
                    )
                    batch_futures.append(task)

                # Create a task that waits for all futures in this batch
                batch_task = asyncio.gather(*batch_futures, return_exceptions=True)
                batch_tasks.append(batch_task)

            # Wait for all batch tasks to complete, with optional timeout
            try:
                if timeout is not None:
                    batch_results = await asyncio.wait_for(
                        asyncio.gather(*batch_tasks, return_exceptions=True),
                        timeout=timeout,
                    )
                else:
                    batch_results = await asyncio.gather(
                        *batch_tasks, return_exceptions=True
                    )

                # Flatten and filter batch results
                for batch_result in batch_results:
                    if isinstance(batch_result, Exception):
                        self.logger.error(f"Batch processing error: {batch_result}")
                        continue

                    # Only process non-exception results
                    if isinstance(batch_result, list):
                        for result in batch_result:
                            if not isinstance(result, Exception):
                                results.append(result)
            except asyncio.TimeoutError:
                self.logger.warning(
                    f"Timeout occurred while processing batches (timeout={timeout}s)"
                )

            # Check resource usage after each batch
            self.resource_optimizer.optimize()

        return results

    async def _process_stage_parallel(
        self,
        stage: str,
        models: List[str],
        context: Dict[str, Any],
        pattern_name: str,
        progress_tracker: ProgressTracker,
    ) -> Dict[str, ModelResponse]:
        """
        Process a single stage with multiple models in parallel.

        Args:
            stage: The processing stage
            models: List of models to use
            context: Context with variables for the template
            pattern_name: The analysis pattern to use
            progress_tracker: Progress tracker instance

        Returns:
            Dictionary mapping model names to responses
        """
        # Create stage-specific prompt from template
        prompt = self._create_stage_prompt(stage, context, pattern_name)

        # Create progress update callbacks
        callbacks = {}
        for model_name in models:

            def make_callback(model):
                def callback(update: ProgressUpdate):
                    # Update progress tracker
                    progress_tracker.update(
                        model=update.model,
                        stage=update.stage,
                        status=update.status,
                        message=update.message,
                    )

                return callback

            callbacks[model_name] = make_callback(model_name)

        # Create tasks for all models
        tasks = {}
        for model_name in models:
            tasks[model_name] = self.get_model_response(
                model_name=model_name,
                prompt=prompt,
                stage=stage,
                progress_callback=callbacks[model_name],
            )

        # Execute all tasks concurrently
        responses = {}
        # Use asyncio.as_completed to process responses as they arrive
        pending_tasks = list(tasks.items())
        for future in asyncio.as_completed(list(tasks.values())):
            try:
                response = await future
                # Find the model name that corresponds to this response
                for i, (model_name, task) in enumerate(pending_tasks):
                    if id(task) == id(future):
                        responses[model_name] = response
                        pending_tasks.pop(i)
                        break
            except Exception as e:
                # Since we can't easily map the future back to the model name
                # in the exception case, we'll log the error
                self.logger.error(f"Error in stage {stage}: {e}")

        # Handle any missing responses by logging errors
        for model_name in models:
            if model_name not in responses:
                self.logger.error(f"Error in {model_name} for stage {stage}")
                # Update progress tracker with error
                progress_tracker.update(
                    model=model_name,
                    stage=stage,
                    status=ProgressStatus.ERROR,
                    message="Error: Failed to get response",
                )

        return responses

    def _prepare_stage_context(
        self,
        stage: str,
        previous_responses: Dict[str, Dict[str, Dict[str, ModelResponse]]],
        original_prompt: str,
    ) -> Dict[str, Any]:
        """
        Prepare context for a stage based on previous stage responses.

        Args:
            stage: Current stage
            previous_responses: Responses from previous stages
            original_prompt: Original user prompt

        Returns:
            Context dictionary for the stage
        """
        context = {"original_prompt": original_prompt}

        # If this is the first stage, return just the original prompt
        if stage == "initial" or not previous_responses:
            return context

        # Add context from previous stages
        for prev_stage, stage_data in previous_responses.items():
            if "responses" not in stage_data:
                continue

            # Add combined responses
            combined_responses = "\n\n".join(
                [f"Model {m}:\n{r.content}" for m, r in stage_data["responses"].items()]
            )
            context[f"{prev_stage}_responses"] = combined_responses

            # Add individual model responses
            for model, response in stage_data["responses"].items():
                context[f"{model}_{prev_stage}"] = response.content

                # If this stage follows the previous one in the sequence
                if (
                    (prev_stage == "initial" and stage == "meta")
                    or (prev_stage == "meta" and stage == "hyper")
                    or (prev_stage == "hyper" and stage == "ultra")
                ):
                    # Set current model's own previous response
                    context["own_response"] = (
                        response.content
                        if prev_stage == "initial"
                        else context.get("own_response", "")
                    )
                    context["own_meta"] = (
                        response.content
                        if prev_stage == "meta"
                        else context.get("own_meta", "")
                    )

                    # Set other models' responses
                    other_responses = "\n\n".join(
                        [
                            f"Model {m}:\n{r.content}"
                            for m, r in stage_data["responses"].items()
                            if m != model
                        ]
                    )
                    context["other_responses"] = (
                        other_responses
                        if prev_stage == "initial"
                        else context.get("other_responses", "")
                    )
                    context["other_meta_responses"] = (
                        other_responses
                        if prev_stage == "meta"
                        else context.get("other_meta_responses", "")
                    )

        return context

    async def process_with_pattern(
        self,
        prompt: str,
        pattern_name: Optional[str] = None,
        models: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        use_parallel: bool = True,  # Enable parallel processing by default
    ) -> Dict[str, Any]:
        """
        Process a prompt using a specific analysis pattern.

        Args:
            prompt: The prompt to process
            pattern_name: Name of the analysis pattern (default: config.default_pattern)
            models: Specific models to use (default: all registered models)
            progress_callback: Optional callback for progress updates
            use_parallel: Whether to use parallel processing for stages

        Returns:
            Dictionary with results from each stage

        Raises:
            ValueError: If the pattern doesn't exist or no valid responses are received
        """
        # Use default pattern if none specified
        pattern_name = pattern_name or self.config.default_pattern

        # Get the pattern
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            available_patterns = list(self.patterns.keys())
            error_msg = (
                f"Unknown pattern: {pattern_name}. "
                f"Available patterns: {available_patterns}"
            )
            raise ValueError(error_msg)

        # If models is specified, validate that they exist
        if models:
            invalid_models = [m for m in models if m not in self.model_registry]
            if invalid_models:
                raise ValueError(f"Invalid model(s) specified: {invalid_models}")

        # Get prioritized list of models
        prioritized_models = self.get_prioritized_models(models)
        if not prioritized_models:
            raise ValueError("No models available for processing")

        # Set up progress tracking
        progress_tracker = ProgressTracker(pattern.stages)

        # Set up progress callback if provided
        if progress_callback:

            def callback(update: ProgressUpdate):
                summary = progress_tracker.get_summary()
                progress_callback(summary)

            progress_tracker.add_callback(callback)

        self.logger.info(
            f"Starting process_with_pattern using pattern '{pattern_name}', "
            f"stages: {pattern.stages}, models: {prioritized_models}"
        )

        # Initialize results
        results = {
            "pattern": pattern_name,
            "stages": {},
            "original_prompt": prompt,
        }

        # Track responses for context management
        stage_responses = {}

        # Process each stage
        for stage in pattern.stages:
            # Prepare context for this stage
            context = self._prepare_stage_context(
                stage=stage,
                previous_responses=stage_responses,
                original_prompt=prompt,
            )

            # Process stage (parallel or sequential)
            if use_parallel and self.config.parallel_processing:
                stage_result = await self._process_stage_parallel(
                    stage=stage,
                    models=prioritized_models,
                    context=context,
                    pattern_name=pattern_name,
                    progress_tracker=progress_tracker,
                )
            else:
                stage_result = await self._process_stage(
                    stage=stage,
                    models=prioritized_models,
                    context=context,
                    pattern_name=pattern_name,
                    progress_tracker=progress_tracker,
                )

            if not stage_result:
                error_message = f"No valid responses received for stage '{stage}'"
                self.logger.error(error_message)
                results["stages"][stage] = {"error": error_message, "responses": {}}
                continue

            # Store the responses for results and context
            stage_responses[stage] = {"responses": stage_result}

            # Format the responses for the results
            results["stages"][stage] = {
                "responses": {
                    model: response.content for model, response in stage_result.items()
                },
                "metadata": {
                    model: {
                        "quality": response.quality.__dict__,
                        "tokens": response.tokens_used,
                        "timestamp": response.timestamp,
                    }
                    for model, response in stage_result.items()
                },
            }

        # Add overall progress information
        results["progress"] = progress_tracker.get_summary()

        return results

    def _validate_model_compatibility(
        self, task_requirements: Dict[str, Any]
    ) -> List[str]:
        """
        Validates which models are compatible with specific task requirements.

        Args:
            task_requirements: Dictionary of required capabilities

        Returns:
            List of compatible model names
        """
        compatible_models = []

        for name, registration in self.model_registry.items():
            # Check if the model meets all requirements
            meets_requirements = True

            for requirement, value in task_requirements.items():
                if requirement == "min_tokens":
                    # Special case for minimum token capability
                    if registration.capabilities.get("max_tokens", 0) < value:
                        meets_requirements = False
                        break
                elif requirement == "tags":
                    # Check if model has all required tags
                    if not all(tag in registration.tags for tag in value):
                        meets_requirements = False
                        break
                else:
                    # General capability check
                    if registration.capabilities.get(requirement) != value:
                        meets_requirements = False
                        break

            if meets_requirements:
                compatible_models.append(name)

        return compatible_models

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get orchestrator metrics.

        Returns:
            Dictionary with orchestrator metrics
        """
        metrics = {}

        if not self.config.collect_metrics:
            return metrics

        # Calculate average response time
        avg_response_time = (
            sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            if self.metrics["response_times"]
            else 0
        )

        # Calculate success rates
        success_rates = {}
        for model, stats in self.metrics["success_rates"].items():
            success_rate = (
                stats["success"] / stats["total"] if stats["total"] > 0 else 0
            )
            success_rates[model] = success_rate

        # Average quality scores
        quality_scores = {}
        for model, scores in self.metrics["quality_scores"].items():
            avg_score = sum(scores) / len(scores) if scores else 0
            quality_scores[model] = avg_score

        # Combine metrics
        metrics = {
            "avg_response_time_ms": avg_response_time * 1000,  # Convert to ms
            "success_rates": success_rates,
            "token_usage": self.metrics["token_usage"],
            "quality_scores": quality_scores,
        }

        # Add cache metrics if available
        if self.cache:
            cache_metrics = self.cache.get_metrics()
            metrics["cache"] = cache_metrics

        # Add circuit breaker metrics if enabled
        if self.config.circuit_breaker_enabled:
            metrics["circuit_breakers"] = self.circuit_breakers.get_all_status()

        # Add resource metrics
        metrics["resources"] = {
            "cpu_percent": self.resource_optimizer.current_metrics.cpu_percent,
            "memory_percent": self.resource_optimizer.current_metrics.memory_percent,
            "memory_used_mb": self.resource_optimizer.current_metrics.memory_used_mb,
            "memory_avail_mb": self.resource_optimizer.current_metrics.memory_available_mb,
            "concurrency": self.resource_optimizer.concurrency_config.current_concurrency,
        }

        return metrics

    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            "response_times": [],
            "success_rates": {},
            "token_usage": {},
            "quality_scores": {},
        }
        self.logger.info("Reset all metrics")

    def clear_cache(self):
        """Clear the response cache."""
        if self.cache:
            self.cache.clear_expired()
            self.logger.info("Cleared response cache")

    def reset_circuit_breakers(self):
        """Reset all circuit breakers."""
        if self.config.circuit_breaker_enabled:
            # Create a new registry (simplest way to reset all)
            self.circuit_breakers = CircuitBreakerRegistry()
            self.logger.info("Reset all circuit breakers")

    async def process_with_analysis_mode(
        self,
        prompt: str,
        mode: str = "standard",
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Process a prompt using a predefined analysis mode.

        Args:
            prompt: The prompt to process
            mode: Name of the analysis mode to use (must be defined in config)
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with results from processing

        Raises:
            ValueError: If the specified mode doesn't exist
        """
        if mode not in self.config.analysis_modes:
            available_modes = list(self.config.analysis_modes.keys())
            raise ValueError(
                f"Unknown analysis mode: {mode}. Available modes: {available_modes}"
            )

        # Get the mode configuration
        mode_config = self.config.analysis_modes[mode]

        # Select models based on strategy
        models_to_use = mode_config.models
        if models_to_use is None:
            if mode_config.model_selection_strategy == "all":
                models_to_use = list(self.model_registry.keys())
            elif mode_config.model_selection_strategy == "best":
                # Use models with highest weights up to max_workers
                models_to_use = self.get_prioritized_models()
                if self.config.max_workers:
                    models_to_use = models_to_use[: self.config.max_workers]
            elif mode_config.model_selection_strategy == "random":
                # Use random selection of models
                import random

                available_models = list(self.model_registry.keys())
                num_models = min(
                    len(available_models),
                    self.config.max_workers or len(available_models),
                )
                models_to_use = random.sample(available_models, num_models)
            else:  # weighted (default)
                models_to_use = self.get_prioritized_models()

        # Process with the selected configuration
        result = await self.process_with_pattern(
            prompt=prompt,
            pattern_name=mode_config.pattern,
            models=models_to_use,
            progress_callback=progress_callback,
            use_parallel=self.config.parallel_processing,
        )

        # Add mode information to result
        result["mode"] = mode
        result["mode_config"] = {
            "pattern": mode_config.pattern,
            "models": models_to_use,
            "strategy": mode_config.model_selection_strategy,
        }

        return result

    def add_analysis_mode(self, mode: AnalysisMode) -> None:
        """
        Add or update an analysis mode.

        Args:
            mode: The analysis mode to add or update
        """
        self.config.analysis_modes[mode.name] = mode
        self.logger.info(f"Added analysis mode: {mode.name}")

    def get_available_analysis_modes(self) -> List[str]:
        """
        Get list of available analysis modes.

        Returns:
            List of analysis mode names
        """
        return list(self.config.analysis_modes.keys())

    def get_best_response(
        self, result: Dict[str, Any], stage: str = "ultra"
    ) -> Optional[str]:
        """
        Get the best response from a pattern-based analysis result.

        Args:
            result: Result dictionary from process_with_pattern
            stage: Stage to get response from (default: "ultra" for final synthesis)

        Returns:
            The best response content, or None if not available
        """
        if (
            "stages" not in result
            or stage not in result["stages"]
            or "responses" not in result["stages"][stage]
            or not result["stages"][stage]["responses"]
        ):
            self.logger.warning(f"No responses found for stage '{stage}'")
            return None

        responses = result["stages"][stage]["responses"]

        # If only one response, return it
        if len(responses) == 1:
            return next(iter(responses.values()))

        # If multiple responses, try to find the best one based on quality
        if "metadata" in result["stages"][stage]:
            metadata = result["stages"][stage]["metadata"]
            best_model = None
            best_score = -1

            for model, meta in metadata.items():
                if "quality" in meta:
                    quality = meta["quality"]
                    if isinstance(quality, dict):
                        # Calculate average score
                        score = sum(float(v) for v in quality.values()) / len(quality)
                        if score > best_score:
                            best_score = score
                            best_model = model

            if best_model and best_model in responses:
                return responses[best_model]

        # Fallback: return the response from the highest-weighted model
        prioritized_models = self.get_prioritized_models()
        for model in prioritized_models:
            if model in responses:
                return responses[model]

        # Last resort: return any response
        return next(iter(responses.values()))

    async def quick_analyze(
        self,
        prompt: str,
        analysis_type: str = "standard",
    ) -> str:
        """
        Quick helper method to analyze a prompt and return the best result.

        Args:
            prompt: The prompt to analyze
            analysis_type: Type of analysis to perform (mode or pattern name)

        Returns:
            The best response content
        """
        # Check if analysis_type is a mode or pattern
        if analysis_type in self.config.analysis_modes:
            # It's a mode
            result = await self.process_with_analysis_mode(prompt, mode=analysis_type)
        elif analysis_type in self.patterns:
            # It's a pattern
            result = await self.process_with_pattern(prompt, pattern_name=analysis_type)
        else:
            # Default to standard mode
            self.logger.warning(
                f"Unknown analysis type '{analysis_type}', using standard mode"
            )
            result = await self.process_with_analysis_mode(prompt, mode="standard")

        return self.get_best_response(result) or "No valid response generated"

    async def compare_analyses(
        self,
        prompt: str,
        analysis_types: List[str],
    ) -> Dict[str, Any]:
        """
        Compare multiple analysis approaches on the same prompt.

        Args:
            prompt: The prompt to analyze
            analysis_types: List of analysis types (modes or patterns)

        Returns:
            Dictionary with comparative results
        """
        results = {}
        comparison = {
            "prompt": prompt,
            "analyses": {},
            "summary": {},
        }

        # Run each analysis
        for analysis_type in analysis_types:
            if analysis_type in self.config.analysis_modes:
                # It's a mode
                result = await self.process_with_analysis_mode(
                    prompt, mode=analysis_type
                )
                results[analysis_type] = result
                comparison["analyses"][analysis_type] = {
                    "type": "mode",
                    "response": self.get_best_response(result),
                    "pattern": result.get("pattern"),
                    "models_used": len(result.get("mode_config", {}).get("models", [])),
                }
            elif analysis_type in self.patterns:
                # It's a pattern
                result = await self.process_with_pattern(
                    prompt, pattern_name=analysis_type
                )
                results[analysis_type] = result
                comparison["analyses"][analysis_type] = {
                    "type": "pattern",
                    "response": self.get_best_response(result),
                    "pattern": analysis_type,
                    "models_used": len(
                        result.get("stages", {}).get("ultra", {}).get("responses", {})
                    ),
                }
            else:
                self.logger.warning(f"Skipping unknown analysis type: {analysis_type}")

        # Generate comparative metrics
        total_tokens = 0
        for analysis_type, result in results.items():
            analysis_tokens = 0
            for stage in result.get("stages", {}).values():
                for meta in stage.get("metadata", {}).values():
                    analysis_tokens += meta.get("tokens", 0)
            comparison["analyses"][analysis_type]["tokens"] = analysis_tokens
            total_tokens += analysis_tokens

        comparison["summary"] = {
            "total_tokens": total_tokens,
            "analysis_count": len(results),
        }

        return comparison

    def _retry_on_failure(self, func, *args, **kwargs):
        """Retry a function with exponential backoff."""
        max_retries = self.config.max_retries
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                wait_time = (2**attempt) * self.config.retry_base_delay
                self.logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                    f"Retrying in {wait_time}s"
                )
                time.sleep(wait_time)

                if attempt == max_retries - 1:
                    raise

    def process_with_fault_tolerance(self, data, pattern=None):
        """Process data with circuit breaker pattern for fault tolerance."""
        # Create a default circuit breaker for this operation
        circuit = self.circuit_breakers.get_or_create(
            "global",
            failure_threshold=self.config.failure_threshold,
            recovery_timeout=self.config.recovery_timeout,
        )

        if not circuit.allow_request():
            self.logger.warning("Circuit breaker is open. Skipping processing.")
            return None

        try:
            return self.process_with_pattern(data, pattern)
        except Exception as e:
            circuit.record_failure()
            self.logger.error(f"Processing failed: {str(e)}")
            return None

    async def stream_model_response(
        self,
        model_name: str,
        prompt: str,
        stage: str,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Get a streaming response from a model.

        Args:
            model_name: Name of the registered model
            prompt: The prompt to send
            stage: The processing stage
            progress_callback: Optional callback for progress updates

        Yields:
            Dictionary with streaming update information

        Raises:
            ValueError: If the model doesn't exist
            RuntimeError: If the request fails
        """
        # Check resource status before streaming
        resource_metrics = self.resource_optimizer.get_current_metrics()
        if resource_metrics.memory_percent > 90:
            self.logger.warning(
                "High memory usage detected before streaming. Optimizing resources."
            )
            self.resource_optimizer.optimize()

        # Check if model exists
        if model_name not in self.model_registry:
            raise ValueError(f"Model not found: {model_name}")

        # Get model registration
        registration = self.model_registry[model_name]
        adapter = registration.adapter

        # Check if the response is in the cache and cache supports streaming
        supports_streaming = False
        cached_stream = None

        # Try to use streaming cache if available
        if self.config.cache_enabled and self.cache:
            # Check if the cache supports streaming methods safely
            try:
                # Generate cache key for streaming
                prompt_hash = hashlib.md5(
                    prompt.encode(), usedforsecurity=False
                ).hexdigest()

                # Try to access the stream methods safely
                if hasattr(self.cache, "generate_stream_cache_key"):
                    cache_key = self.cache.generate_stream_cache_key(
                        model_name, stage, prompt_hash
                    )

                    # Try to get from stream cache
                    if hasattr(self.cache, "get_stream"):
                        cached_stream = await self.cache.get_stream(cache_key)
                        supports_streaming = True
            except Exception as e:
                self.logger.warning(f"Stream cache access failed: {e}")

        # Use cached stream if available
        if cached_stream:
            self.logger.info(f"Stream cache hit for {model_name}")

            if progress_callback:
                progress_callback(
                    ProgressUpdate(
                        model=model_name,
                        stage=stage,
                        status=ProgressStatus.STARTED,
                        message="Retrieved from cache",
                    )
                )

            # Return cached chunks
            full_content = ""
            progress = 0.0

            async for chunk in cached_stream:
                full_content += chunk

                # Estimate progress (approximate)
                progress += 5.0  # Faster progress for cached content
                progress = min(progress, 99.0)  # Cap at 99% until done

                if progress_callback:
                    progress_callback(
                        ProgressUpdate(
                            model=model_name,
                            stage=stage,
                            status=ProgressStatus.IN_PROGRESS,
                            message="Receiving from cache",
                        )
                    )

                yield {
                    "model": model_name,
                    "content": chunk,
                    "done": False,
                    "stage": stage,
                    "progress": progress,
                    "cached": True,
                }

            # Final update with complete content
            if progress_callback:
                progress_callback(
                    ProgressUpdate(
                        model=model_name,
                        stage=stage,
                        status=ProgressStatus.COMPLETED,
                        message="Cache retrieval complete",
                    )
                )

            yield {
                "model": model_name,
                "content": full_content,
                "done": True,
                "stage": stage,
                "progress": 100.0,
                "cached": True,
            }

            return

        # Check if the model supports streaming
        capabilities = adapter.get_capabilities()
        supports_streaming = capabilities.get("supports_streaming", False)

        if not supports_streaming:
            # For models that don't support streaming, get the full response
            # and yield it as a single chunk
            if progress_callback:
                progress_callback(
                    ProgressUpdate(
                        model=model_name,
                        stage=stage,
                        status=ProgressStatus.STARTED,
                        message="Starting request",
                    )
                )

            try:
                response = await adapter.generate(prompt)

                if progress_callback:
                    progress_callback(
                        ProgressUpdate(
                            model=model_name,
                            stage=stage,
                            status=ProgressStatus.COMPLETED,
                            message="Request completed",
                        )
                    )

                yield {
                    "model": model_name,
                    "content": response,
                    "done": True,
                    "stage": stage,
                    "progress": 100.0,
                    "cached": False,
                }

            except Exception as e:
                self.logger.error(f"Error getting response from {model_name}: {e}")

                if progress_callback:
                    progress_callback(
                        ProgressUpdate(
                            model=model_name,
                            stage=stage,
                            status=ProgressStatus.FAILED,
                            message=f"Request failed: {e}",
                        )
                    )

                raise RuntimeError(f"Failed to get response from {model_name}: {e}")

        else:
            # Stream the response for models that support it
            if progress_callback:
                progress_callback(
                    ProgressUpdate(
                        model=model_name,
                        stage=stage,
                        status=ProgressStatus.STARTED,
                        message="Starting streaming request",
                    )
                )

            full_content = ""
            progress = 0.0
            all_chunks = []

            try:
                # Use the stream_generate method
                async for chunk in adapter.stream_generate(prompt):
                    full_content += chunk
                    all_chunks.append(chunk)

                    # Estimate progress (approximate)
                    progress += 2.0  # Increment by small amount
                    progress = min(progress, 99.0)  # Cap at 99% until done

                    if progress_callback:
                        progress_callback(
                            ProgressUpdate(
                                model=model_name,
                                stage=stage,
                                status=ProgressStatus.IN_PROGRESS,
                                message="Receiving stream",
                            )
                        )

                    yield {
                        "model": model_name,
                        "content": chunk,
                        "done": False,
                        "stage": stage,
                        "progress": progress,
                        "cached": False,
                    }

                # Final update with the full content
                if progress_callback:
                    progress_callback(
                        ProgressUpdate(
                            model=model_name,
                            stage=stage,
                            status=ProgressStatus.COMPLETED,
                            message="Stream completed",
                        )
                    )

                yield {
                    "model": model_name,
                    "content": full_content,
                    "done": True,
                    "stage": stage,
                    "progress": 100.0,
                    "cached": False,
                }

                # Cache the streaming response if cache supports it
                if (
                    self.config.cache_enabled
                    and self.cache
                    and supports_streaming
                    and hasattr(self.cache, "set_stream")
                ):
                    try:
                        # Generate cache key
                        prompt_hash = hashlib.md5(
                            prompt.encode(), usedforsecurity=False
                        ).hexdigest()

                        # Get the cache key and prepare response info
                        cache_key = self.cache.generate_stream_cache_key(
                            model_name, stage, prompt_hash
                        )

                        # Prepare response info for TTL calculation
                        response_info = {
                            "model": model_name,
                            "stage": stage,
                            "prompt": prompt,
                            "tokens_used": len(full_content.split())
                            * 1.33,  # Rough estimate
                        }

                        # Cache the stream
                        await self.cache.set_stream(
                            cache_key, all_chunks, response_info
                        )
                        self.logger.info(f"Cached streaming response for {model_name}")
                    except Exception as e:
                        self.logger.warning(f"Failed to cache stream response: {e}")

            except Exception as e:
                self.logger.error(f"Error streaming response from {model_name}: {e}")

                if progress_callback:
                    progress_callback(
                        ProgressUpdate(
                            model=model_name,
                            stage=stage,
                            status=ProgressStatus.FAILED,
                            message=f"Stream failed: {e}",
                        )
                    )

                raise RuntimeError(f"Failed to stream response from {model_name}: {e}")

    async def stream_process(
        self,
        prompt: str,
        pattern: Optional[str] = None,
        max_tokens: Optional[int] = None,
        models: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a prompt with streaming responses.

        Args:
            prompt: The prompt to process
            pattern: The pattern to use (default: config.default_pattern)
            max_tokens: Maximum tokens to generate (optional)
            models: Specific models to use (default: all registered models)

        Yields:
            Dictionary updates with streaming content

        Raises:
            ValueError: If no models are available or pattern doesn't exist
        """
        # Use default pattern if none specified
        pattern_name = pattern or self.config.default_pattern

        # Get the pattern
        pattern_config = self.patterns.get(pattern_name)
        if not pattern_config:
            available_patterns = list(self.patterns.keys())
            error_msg = (
                f"Unknown pattern: {pattern_name}. "
                f"Available patterns: {available_patterns}"
            )
            raise ValueError(error_msg)

        # If models is specified, validate that they exist
        if models:
            invalid_models = [m for m in models if m not in self.model_registry]
            if invalid_models:
                raise ValueError(f"Invalid model(s) specified: {invalid_models}")

        # Get prioritized list of models
        prioritized_models = self.get_prioritized_models(models)
        if not prioritized_models:
            raise ValueError("No models available for processing")

        # For streaming, we'll use only the first stage of the pattern
        # and only one model (the highest priority one)
        stage = pattern_config.stages[0]
        selected_model = prioritized_models[0]

        # Prepare context for this stage (simplified for streaming)
        context = {"original_prompt": prompt}

        # Create stage-specific prompt from template
        stage_prompt = self._create_stage_prompt(stage, context, pattern_name)

        # Placeholder for processed prompt (normally would go through more processing)
        processed_prompt = stage_prompt

        # Stream the response
        self.logger.info(
            f"Starting stream_process using pattern '{pattern_name}', "
            f"stage: {stage}, model: {selected_model}"
        )

        progress = 0.0

        async for update in self.stream_model_response(
            model_name=selected_model,
            prompt=processed_prompt,
            stage=stage,
        ):
            # Update progress based on the update
            done = update.get("done", False)
            progress = update.get("progress", progress)

            # Add additional context to the update
            enriched_update = {
                **update,
                "pattern": pattern_name,
                "total_progress": progress,
            }

            yield enriched_update

            # Stop if done
            if done:
                break

        # If we have a multi-stage pattern, provide a final summary update
        if len(pattern_config.stages) > 1:
            message = (
                f"Streaming complete. Full analysis would include "
                f"{len(pattern_config.stages)} stages."
            )
            yield {
                "model": selected_model,
                "content": "",
                "done": True,
                "stage": "summary",
                "progress": 100.0,
                "pattern": pattern_name,
                "total_progress": 100.0,
                "message": message,
            }

    async def process_with_resource_awareness(
        self,
        prompt: str,
        pattern_name: Optional[str] = None,
        models: Optional[List[str]] = None,
        memory_requirement_mb: Optional[float] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Process a prompt with resource awareness.

        Args:
            prompt: The prompt to process
            pattern_name: Name of the analysis pattern (default: config.default_pattern)
            models: Specific models to use (default: all registered models)
            memory_requirement_mb: Estimated memory requirement in MB
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with results from processing
        """

        # Use resource-aware scheduling
        async def process_task():
            return await self.process_with_pattern(
                prompt=prompt,
                pattern_name=pattern_name,
                models=models,
                progress_callback=progress_callback,
            )

        return await self.resource_optimizer.schedule_resource_aware(
            process_task,
            memory_requirement_mb=memory_requirement_mb,
        )

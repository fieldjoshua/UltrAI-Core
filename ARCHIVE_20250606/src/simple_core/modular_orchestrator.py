"""
Modular orchestrator with pluggable analysis modules.

This builds on the enhanced orchestrator to add support for
pluggable analysis modules.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Type

from .adapter import Adapter
from .analysis.analysis_manager import AnalysisManager
from .analysis.analysis_module import AnalysisModule
from .analysis.modules.comparative import ComparativeAnalysis
from .analysis.modules.factual import FactualAnalysis
from .cache_service import CacheService
from .config import Config, ModelDefinition
from .config.analysis_config import AnalysisConfig
from .config.request_config import RequestConfig
from .enhanced_orchestrator import EnhancedResponse
from .prompt_templates import PromptTemplates
from .quality_metrics import QualityMetrics

logger = logging.getLogger(__name__)


class ModularOrchestrator:
    """
    Orchestrator with pluggable analysis modules.

    This orchestrator extends the enhanced orchestrator with support for
    selecting different analysis strategies.
    """

    # Registry of available analysis modules
    ANALYSIS_MODULES = {
        "comparative": ComparativeAnalysis,
        "factual": FactualAnalysis,
    }

    def __init__(
        self,
        models: List[Tuple[ModelDefinition, Adapter]],
        config: Config,
        analysis_config: Optional[AnalysisConfig] = None,
        prompt_templates: Optional[PromptTemplates] = None,
        quality_metrics: Optional[QualityMetrics] = None,
        cache_service: Optional[CacheService] = None,
    ):
        """
        Initialize the modular orchestrator.

        Args:
            models: List of (model_definition, adapter) tuples
            config: Orchestrator configuration
            analysis_config: Analysis configuration
            prompt_templates: Templates for different stages of processing
            quality_metrics: Service for evaluating response quality
            cache_service: Service for caching responses
        """
        self.models = models
        self.config = config

        # Ensure the models are sorted by priority
        self.models.sort(key=lambda x: x[0].priority)

        # Set the analysis configuration
        self.analysis_config = analysis_config or AnalysisConfig.create_default()

        # Create the analysis manager
        weights = {self.analysis_config.analysis_type: 1.0}
        self.analysis_manager = AnalysisManager(
            enabled_modules=[self.analysis_config.analysis_type],
            weights=weights,
            module_registry=self.ANALYSIS_MODULES,
        )

        # Initialize support services
        self.prompt_templates = prompt_templates or PromptTemplates()
        self.quality_metrics = quality_metrics or QualityMetrics()
        self.cache_service = cache_service

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request through the orchestrator.

        This method can accept either a raw dictionary or a RequestConfig object.

        Args:
            request: Dictionary with the request or a RequestConfig object

        Returns:
            Dictionary with processed results
        """
        # Convert RequestConfig to dictionary if needed
        if isinstance(request, RequestConfig):
            request = request.to_dict()

        # Get the prompt from the request
        prompt = request.get("prompt")
        if not prompt:
            raise ValueError("Request must contain a 'prompt' key")

        # Get model filtering
        model_names = request.get("model_names", [])
        lead_model = request.get("lead_model")

        # Get analysis configuration
        analysis_type = request.get("analysis_type", self.analysis_config.analysis_type)

        # Generate cache key
        cache_key = f"{prompt}_{','.join(model_names)}_{lead_model}_{analysis_type}"

        # Check cache if available
        if self.cache_service:
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for prompt: {prompt[:30]}...")
                return cached_result

        # Filter models if needed
        models_to_use = self.models
        if model_names:
            models_to_use = [
                (model_def, adapter)
                for model_def, adapter in self.models
                if model_def.name in model_names
            ]

            if not models_to_use:
                raise ValueError(f"No models found matching names: {model_names}")

        # Determine lead model (synthesis model)
        synthesis_model = None
        if lead_model:
            for model_def, adapter in models_to_use:
                if model_def.name == lead_model:
                    synthesis_model = (model_def, adapter)
                    break

            if not synthesis_model:
                raise ValueError(f"Lead model not found: {lead_model}")
        else:
            # Use the highest priority model as the lead
            synthesis_model = models_to_use[0]

        # Process the request
        logger.info(
            f"Processing request with {len(models_to_use)} models, lead: {synthesis_model[0].name}"
        )

        # Stage 1: Get initial responses
        initial_responses = await self._get_initial_responses(
            prompt, models_to_use, request
        )

        # Stage 2: Run analysis
        analysis_results = {}
        if self.analysis_config.enabled and initial_responses:
            analysis_results = await self._perform_analysis(
                prompt, initial_responses, analysis_type, synthesis_model, request
            )

        # Stage 3: Synthesize results
        synthesis = await self._synthesize_results(
            prompt, initial_responses, analysis_results, synthesis_model, request
        )

        # Select best individual response
        selected_response = await self._select_best_response(initial_responses)

        # Prepare result
        result = {
            "prompt": prompt,
            "initial_responses": [
                {
                    "model": r.model_name,
                    "provider": r.provider,
                    "response": r.response,
                    "response_time": r.response_time,
                    "quality_score": r.quality_score,
                }
                for r in initial_responses
            ],
            "analysis_results": analysis_results,
            "synthesis": synthesis,
            "selected_response": selected_response,
            "lead_model": synthesis_model[0].name,
        }

        # Cache result if caching is enabled
        if self.cache_service:
            await self.cache_service.set(cache_key, result)

        return result

    async def _get_initial_responses(
        self,
        prompt: str,
        models: List[Tuple[ModelDefinition, Adapter]],
        request: Dict[str, Any],
    ) -> List[EnhancedResponse]:
        """Get initial responses from all configured models."""

        # Format the prompt using the initial prompt template
        formatted_prompt = self.prompt_templates.format_initial_prompt(prompt, request)

        # Execute with all configured models
        if self.config.parallel:
            tasks = [
                self._process_with_model(model_def, adapter, formatted_prompt, request)
                for model_def, adapter in models
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            responses = []
            for model_def, adapter in models:
                try:
                    response = await self._process_with_model(
                        model_def, adapter, formatted_prompt, request
                    )
                    responses.append(response)
                except Exception as e:
                    logger.error(f"Error processing with {model_def.name}: {str(e)}")
                    responses.append(e)

        # Filter out exceptions and convert to EnhancedResponse
        valid_responses = []
        for i, response_or_error in enumerate(responses):
            if isinstance(response_or_error, Exception):
                model_name = models[i][0].name
                logger.error(f"Model {model_name} failed: {str(response_or_error)}")
                continue

            model_def = models[i][0]
            response = response_or_error

            # Calculate quality score if quality metrics are available
            quality_score = None
            if self.quality_metrics:
                quality_score = await self.quality_metrics.evaluate(
                    prompt, response["response"], model_def.name
                )

            enhanced_response = EnhancedResponse(
                model_name=model_def.name,
                response=response["response"],
                provider=model_def.provider,
                response_time=response["time"],
                quality_score=quality_score,
            )
            valid_responses.append(enhanced_response)

        return valid_responses

    async def _perform_analysis(
        self,
        prompt: str,
        responses: List[EnhancedResponse],
        analysis_type: str,
        lead_model: Tuple[ModelDefinition, Adapter],
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Perform analysis on initial responses using the specified module."""
        if not responses:
            return {}

        # Skip analysis if only one response is available
        if len(responses) <= 1:
            return {}

        # Prepare the responses for analysis
        response_dicts = []
        for resp in responses:
            response_dicts.append(
                {
                    "model": resp.model_name,
                    "provider": resp.provider,
                    "response": resp.response,
                    "response_time": resp.response_time,
                    "quality_score": resp.quality_score,
                }
            )

        # Configure analysis options
        options = {
            "analysis_model": lead_model[1],
            "lead_model_name": lead_model[0].name,
        }

        # Add any additional options from the request
        if request.get("options") and isinstance(request["options"], dict):
            options.update(request["options"])

        # Run the analysis
        try:
            logger.info(f"Running analysis with module type: {analysis_type}")
            analysis_results = await self.analysis_manager.analyze(
                prompt=prompt, responses=response_dicts, options=options
            )
            return analysis_results
        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
            return {"error": str(e)}

    async def _synthesize_results(
        self,
        prompt: str,
        initial_responses: List[EnhancedResponse],
        analysis_results: Dict[str, Any],
        synthesis_model: Tuple[ModelDefinition, Adapter],
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize initial responses and analysis results into a final response."""
        if not initial_responses:
            return {"response": "", "model": "", "provider": ""}

        # Use the first response if only one is available
        if len(initial_responses) == 1 and not analysis_results:
            r = initial_responses[0]
            return {
                "response": r.response,
                "model": r.model_name,
                "provider": r.provider,
            }

        # Format synthesis prompt
        synthesis_prompt = self._format_synthesis_prompt(
            prompt, initial_responses, analysis_results, request
        )

        # Get synthesis model
        model_def, adapter = synthesis_model

        try:
            synthesis_response = await self._process_with_model(
                model_def, adapter, synthesis_prompt, request, is_synthesis=True
            )

            return {
                "response": synthesis_response["response"],
                "model": model_def.name,
                "provider": model_def.provider,
                "time": synthesis_response["time"],
            }
        except Exception as e:
            logger.error(f"Synthesis with {model_def.name} failed: {str(e)}")
            # Fall back to best individual response if synthesis fails
            best_response = await self._select_best_response(initial_responses)
            return best_response

    def _format_synthesis_prompt(
        self,
        prompt: str,
        responses: List[EnhancedResponse],
        analysis_results: Dict[str, Any],
        request: Dict[str, Any],
    ) -> str:
        """Format the synthesis prompt with responses and analysis."""
        # Format the responses for inclusion
        response_text = ""
        for i, resp in enumerate(responses, 1):
            response_text += (
                f"Response {i} (from {resp.model_name}):\n{resp.response}\n\n"
            )

        # Format the analysis results if available
        analysis_text = ""
        if analysis_results and "combined_summary" in analysis_results:
            analysis_text = f"Analysis:\n{analysis_results['combined_summary']}\n\n"
        else:
            analysis_text = "No detailed analysis available.\n\n"

        # Create the synthesis prompt
        return f"""
You are a helpful assistant creating an optimal response based on multiple AI models' answers to the same prompt.

Original Prompt:
{prompt}

Responses from different models:
{response_text}

{analysis_text}

Your task is to synthesize an optimal response that:
1. Combines the strengths of each response
2. Addresses weaknesses identified in the analysis
3. Resolves any contradictions between responses
4. Provides the most helpful, accurate, and comprehensive answer possible

Create a response that would be better than any of the individual responses alone.
Do not mention that this is a synthesis or that you are combining multiple responses.
Simply provide the best possible answer to the original prompt.
"""

    async def _select_best_response(
        self, responses: List[EnhancedResponse]
    ) -> Dict[str, Any]:
        """Select the best individual response based on quality metrics or priority."""
        if not responses:
            return {"response": "", "model": "", "provider": ""}

        # If quality metrics are available, use them
        if self.quality_metrics and all(r.quality_score is not None for r in responses):
            best_response = max(responses, key=lambda x: x.quality_score or 0)
        else:
            # Fall back to priority-based selection (first in list = highest priority)
            best_response = responses[0]

        return {
            "response": best_response.response,
            "model": best_response.model_name,
            "provider": best_response.provider,
            "quality_score": best_response.quality_score,
        }

    async def _process_with_model(
        self,
        model_def: ModelDefinition,
        adapter: Adapter,
        prompt: str,
        request: Dict[str, Any],
        is_synthesis: bool = False,
    ) -> Dict[str, Any]:
        """Process a request with a single model and return the response."""
        # Get options for the model
        options = request.get("options", {}).copy() if isinstance(request, dict) else {}

        # Add metadata about the processing stage
        if is_synthesis:
            options["processing_stage"] = "synthesis"
        else:
            options["processing_stage"] = "initial"

        # Add model-specific options
        if "model_options" in request and model_def.name in request["model_options"]:
            options.update(request["model_options"][model_def.name])

        # Process with the model
        start_time = time.time()

        try:
            response = await adapter.generate(prompt, options)
            elapsed = time.time() - start_time

            return {"response": response, "time": elapsed}
        except Exception as e:
            logger.error(f"Error with {model_def.name}: {str(e)}")
            raise

"""
Enhanced Orchestrator for Multi-stage LLM Processing
Handles initial responses, meta-analysis, and synthesis

This orchestrator builds on the basic orchestrator to add:
1. Meta-analysis of responses
2. Synthesis of responses and analyses
3. Quality-based model selection
4. Cache integration
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .adapter import Adapter
from .cache_service import CacheService
from .config import Config, ModelDefinition
from .orchestrator import Orchestrator as BaseOrchestrator
from .prompt_templates import PromptTemplates
from .quality_metrics import QualityMetrics

logger = logging.getLogger(__name__)


@dataclass
class EnhancedResponse:
    """Enhanced response with additional metadata and analysis"""

    model_name: str
    response: str
    provider: str
    response_time: float
    quality_score: Optional[float] = None
    meta_analysis: Optional[str] = None


class EnhancedOrchestrator:
    """
    Enhanced orchestrator that provides multi-stage processing:
    1. Initial responses from multiple LLMs
    2. Meta-analysis of responses using selected meta models
    3. Synthesis of responses and analyses using the highest quality model
    """

    def __init__(
        self,
        models: List[Tuple[ModelDefinition, Adapter]],
        config: Config,
        meta_models: Optional[List[Tuple[ModelDefinition, Adapter]]] = None,
        synthesis_model: Optional[Tuple[ModelDefinition, Adapter]] = None,
        prompt_templates: Optional[PromptTemplates] = None,
        quality_metrics: Optional[QualityMetrics] = None,
        cache_service: Optional[CacheService] = None,
    ):
        """
        Initialize the enhanced orchestrator

        Args:
            models: List of (model_definition, adapter) tuples for initial responses
            config: Orchestrator configuration
            meta_models: Models used for meta-analysis (default: use highest priority models from main models)
            synthesis_model: Model used for synthesis (default: use highest priority model from main models)
            prompt_templates: Templates for different stages of processing
            quality_metrics: Service for evaluating response quality
            cache_service: Service for caching responses
        """
        self.models = models
        self.config = config

        # If meta_models not provided, use top models from primary models
        self.meta_models = meta_models or models[: min(2, len(models))]

        # If synthesis_model not provided, use highest priority model
        self.synthesis_model = synthesis_model or models[0]

        # Initialize support services
        self.prompt_templates = prompt_templates or PromptTemplates()
        self.quality_metrics = quality_metrics or QualityMetrics()
        self.cache_service = cache_service

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request through the multi-stage orchestration pipeline

        Args:
            request: Dictionary with the request (must contain 'prompt' key)

        Returns:
            Dictionary with processed results including:
            - initial_responses: All initial model responses
            - meta_analyses: All meta-analyses
            - synthesis: Final synthesized response
            - selected_response: Best individual response
        """
        prompt = request.get("prompt")
        if not prompt:
            raise ValueError("Request must contain a 'prompt' key")

        cache_key = f"{prompt}_{self.config.to_cache_key()}"

        # Check cache if available
        if self.cache_service:
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for prompt: {prompt[:30]}...")
                return cached_result

        # Stage 1: Get initial responses from all models
        logger.info(f"Processing request with {len(self.models)} models")
        initial_responses = await self._get_initial_responses(prompt, request)

        # Stage 2: Run meta-analysis on the responses
        meta_analyses = await self._perform_meta_analysis(
            prompt, initial_responses, request
        )

        # Stage 3: Synthesize results
        synthesis = await self._synthesize_results(
            prompt, initial_responses, meta_analyses, request
        )

        # Select best individual response based on quality metrics
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
            "meta_analyses": [
                {
                    "model": r.model_name,
                    "provider": r.provider,
                    "analysis": r.meta_analysis,
                    "response_time": r.response_time,
                }
                for r in meta_analyses
            ],
            "synthesis": synthesis,
            "selected_response": selected_response,
        }

        # Cache result if caching is enabled
        if self.cache_service:
            await self.cache_service.set(cache_key, result)

        return result

    async def _get_initial_responses(
        self, prompt: str, request: Dict[str, Any]
    ) -> List[EnhancedResponse]:
        """Get initial responses from all configured models"""

        # Format the prompt using the initial prompt template
        formatted_prompt = self.prompt_templates.format_initial_prompt(prompt, request)

        # Execute with all configured models
        if self.config.parallel:
            tasks = [
                self._process_with_model(model_def, adapter, formatted_prompt, request)
                for model_def, adapter in self.models
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            responses = []
            for model_def, adapter in self.models:
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
        for i, (response_or_error) in enumerate(responses):
            if isinstance(response_or_error, Exception):
                logger.error(
                    f"Model {self.models[i][0].name} failed: {str(response_or_error)}"
                )
                continue

            model_def = self.models[i][0]
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

    async def _perform_meta_analysis(
        self,
        prompt: str,
        initial_responses: List[EnhancedResponse],
        request: Dict[str, Any],
    ) -> List[EnhancedResponse]:
        """Perform meta-analysis on initial responses"""
        if not initial_responses:
            return []

        # Skip meta-analysis if only one response is available
        if len(initial_responses) <= 1:
            return []

        # Format meta-analysis prompt with initial responses
        meta_prompt = self.prompt_templates.format_meta_analysis_prompt(
            prompt, initial_responses, request
        )

        meta_analysis_results = []

        # Run meta-analysis with meta models (parallel)
        if self.config.parallel:
            tasks = [
                self._process_with_model(
                    model_def, adapter, meta_prompt, request, is_meta=True
                )
                for model_def, adapter in self.meta_models
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            responses = []
            for model_def, adapter in self.meta_models:
                try:
                    response = await self._process_with_model(
                        model_def, adapter, meta_prompt, request, is_meta=True
                    )
                    responses.append(response)
                except Exception as e:
                    logger.error(
                        f"Error in meta-analysis with {model_def.name}: {str(e)}"
                    )
                    responses.append(e)

        # Process meta-analysis results
        for i, response_or_error in enumerate(responses):
            if isinstance(response_or_error, Exception):
                logger.error(
                    f"Meta model {self.meta_models[i][0].name} failed: {str(response_or_error)}"
                )
                continue

            model_def = self.meta_models[i][0]
            response = response_or_error

            # Add meta analysis to the model's entry
            meta_response = EnhancedResponse(
                model_name=model_def.name,
                response="",  # Not used for meta responses
                provider=model_def.provider,
                response_time=response["time"],
                meta_analysis=response["response"],
            )
            meta_analysis_results.append(meta_response)

        return meta_analysis_results

    async def _synthesize_results(
        self,
        prompt: str,
        initial_responses: List[EnhancedResponse],
        meta_analyses: List[EnhancedResponse],
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize initial responses and meta-analyses into a final response"""
        if not initial_responses:
            return {"response": "", "model": "", "provider": ""}

        # Use the first response if only one is available
        if len(initial_responses) == 1 and not meta_analyses:
            r = initial_responses[0]
            return {
                "response": r.response,
                "model": r.model_name,
                "provider": r.provider,
            }

        # Format synthesis prompt
        synthesis_prompt = self.prompt_templates.format_synthesis_prompt(
            prompt, initial_responses, meta_analyses, request
        )

        # Get synthesis model
        model_def, adapter = self.synthesis_model

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

    async def _select_best_response(
        self, responses: List[EnhancedResponse]
    ) -> Dict[str, Any]:
        """Select the best individual response based on quality metrics or priority"""
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
        is_meta: bool = False,
        is_synthesis: bool = False,
    ) -> Dict[str, Any]:
        """Process a request with a single model and return the response"""
        import time

        # Get options, creating a copy to avoid modifying the original
        options = request.copy() if isinstance(request, dict) else {}

        # Add metadata about the processing stage
        if is_meta:
            options["processing_stage"] = "meta_analysis"
        elif is_synthesis:
            options["processing_stage"] = "synthesis"
        else:
            options["processing_stage"] = "initial"

        start_time = time.time()

        try:
            response = await adapter.generate(prompt, options)
            elapsed = time.time() - start_time

            return {"response": response, "time": elapsed}
        except Exception as e:
            logger.error(f"Error with {model_def.name}: {str(e)}")
            raise

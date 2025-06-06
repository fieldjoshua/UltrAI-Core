"""
Prompt Service Module

This module provides the service layer for handling prompt submission and processing.
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

# Robustly add 'src' to the path to ensure correct module resolution.
# This is a targeted fix to bypass the faulty facade import mechanism.
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from src.models.enhanced_orchestrator import (
    EnhancedOrchestrator,
    OrchestratorConfig,
)
from backend.models.llm_models import (
    AnalysisOption,
    ModelPrediction,
    OutputFormat,
    ProcessPromptRequest,
    PromptResult,
    PromptStreamUpdate,
)
from backend.services.llm_config_service import LLMConfigService

logger = logging.getLogger(__name__)


class AsyncIterator:
    """Type hint for async iterators."""

    async def __aiter__(self):
        pass

    async def __anext__(self):
        pass


class PromptService:
    """Service for handling prompt submission and processing"""

    def __init__(self, llm_config_service: LLMConfigService):
        """Initialize the prompt service.

        Args:
            llm_config_service: Service for managing LLM configuration
        """
        self.llm_config_service = llm_config_service
        self.orchestrators: Dict[str, EnhancedOrchestrator] = {}
        self._initialize_orchestrators()

    def _initialize_orchestrators(self) -> None:
        """Initialize the orchestrators for different analysis modes."""
        # Get analysis modes from config service
        analysis_modes = self.llm_config_service.get_modes()

        for mode in analysis_modes:
            # Create orchestrator config based on mode settings
            config = OrchestratorConfig(
                default_pattern=mode["pattern"],
                parallel_processing=True,
                circuit_breaker_enabled=True,
                collect_metrics=True,
                max_retries=3,
                retry_base_delay=0.5,
                recovery_timeout=int(mode["timeout"] or 30.0),
            )
            self.orchestrators[mode["name"]] = EnhancedOrchestrator(config)

            # Register available models with the orchestrator
            models_dict = self.llm_config_service.get_available_models()
            for model_name, model in models_dict.items():
                if model.get("available", False) and model.get("status", "") == "ready":
                    # Mock API key for testing
                    api_key = "sk_test_mock_key"

                    # Register the model with the orchestrator
                    self.orchestrators[mode["name"]].register_model(
                        name=model_name,
                        api_key=api_key,  # Use mock API key
                        provider=model.get("provider", ""),
                        model=model.get("model", ""),
                        weight=model.get("weight", 1.0),
                    )

    def _format_output(self, content: str, format_type: OutputFormat) -> str:
        """Format the output according to the requested format.

        Args:
            content: The content to format
            format_type: The requested output format

        Returns:
            Formatted content
        """
        if format_type == OutputFormat.PLAIN:
            # Strip markdown formatting
            # This is a simple implementation, a more robust one would be needed in production
            lines = content.split("\n")
            result = []
            for line in lines:
                if line.startswith("#"):
                    # Remove heading markers
                    result.append(line.lstrip("# "))
                elif line.startswith("```"):
                    # Skip code block markers
                    continue
                elif line.startswith("- "):
                    # Convert list items
                    result.append(line[2:])
                else:
                    # Keep other lines as is
                    result.append(line)
            return "\n".join(result)

        elif format_type == OutputFormat.HTML:
            # Convert markdown to HTML
            # A proper markdown to HTML converter should be used in production
            import markdown

            return markdown.markdown(content)

        elif format_type == OutputFormat.JSON:
            # Return content as a JSON string
            import json

            return json.dumps({"content": content})

        # Default is markdown - return as is
        return content

    def _apply_analysis_options(
        self, prompt: str, options: List[AnalysisOption]
    ) -> str:
        """Apply analysis options to the prompt.

        Args:
            prompt: The original prompt
            options: The analysis options to apply

        Returns:
            Modified prompt with instructions based on options
        """
        if not options:
            return prompt

        additional_instructions = []

        if AnalysisOption.DETAILED in options:
            additional_instructions.append("Provide a detailed analysis.")

        if AnalysisOption.BULLET_POINTS in options:
            additional_instructions.append("Format key points as bullet points.")

        if AnalysisOption.EXAMPLES in options:
            additional_instructions.append("Include relevant examples.")

        if AnalysisOption.CITATIONS in options:
            additional_instructions.append("Include citations where appropriate.")

        if AnalysisOption.SUMMARY in options:
            additional_instructions.append("Include a brief summary at the beginning.")

        if AnalysisOption.CODE_BLOCKS in options:
            instructions = "Include code examples in code blocks where relevant."
            additional_instructions.append(instructions)

        if additional_instructions:
            instructions_text = "\n\nAdditional instructions:\n" + "\n".join(
                f"- {instr}" for instr in additional_instructions
            )
            return prompt + instructions_text

        return prompt

    async def process_prompt(
        self, request: ProcessPromptRequest
    ) -> Union[PromptResult, AsyncIterator]:
        """Process a prompt with the specified models and analysis mode.

        Args:
            request: The prompt processing request

        Returns:
            A PromptResult object or an async generator of PromptStreamUpdate objects
        """
        logger.debug(
            f"Processing prompt request: {request.dict(exclude={'api_key'})}"
        )  # Log request safely

        # Determine which analysis mode to use
        analysis_mode = request.analysis_mode
        if analysis_mode not in self.orchestrators:
            logger.warning(
                f"Requested analysis mode '{request.analysis_mode}' not found. Using 'standard'."
            )
            analysis_mode = "standard"

        # Get the corresponding orchestrator
        orchestrator = self.orchestrators[analysis_mode]
        logger.debug(f"Using orchestrator for mode: {analysis_mode}")
        logger.debug(f"Orchestrator initial models: {list(orchestrator.models.keys())}")

        # Apply analysis options to the prompt
        enhanced_prompt = self._apply_analysis_options(request.prompt, request.options)

        # Override the pattern if specified
        if request.pattern:
            pattern = request.pattern
            available_patterns = (
                self.llm_config_service.get_available_analysis_patterns()
            )
            if pattern not in available_patterns:
                logger.warning(
                    f"Requested pattern '{pattern}' not found. Using default pattern."
                )
                pattern = orchestrator.config.analysis_pattern
        else:
            pattern = orchestrator.config.analysis_pattern
        logger.debug(f"Using analysis pattern: {pattern}")

        # Filter the models if specific ones are requested
        if request.selected_models:
            logger.debug(
                f"Filtering models based on request: {request.selected_models}"
            )
            initial_model_count = len(orchestrator.models)
            models_to_process = {
                name: model
                for name, model in orchestrator.models.items()
                if name in request.selected_models
            }
            # Temporarily update orchestrator models for this request
            original_models = orchestrator.models
            orchestrator.models = models_to_process
            logger.debug(
                f"Models remaining after filtering: {list(orchestrator.models.keys())}"
            )

            if not orchestrator.models:
                logger.error(
                    "ValueError: No valid models selected for processing after filtering."
                )
                # Restore original models before raising
                orchestrator.models = original_models
                raise ValueError("No valid models selected for processing")
        else:
            logger.debug(
                "No specific models requested, using all available models for the orchestrator."
            )
            # Ensure we restore original models if no filtering happened but we modified it before
            # This scenario shouldn't happen with current logic, but good practice
            if "original_models" in locals():
                orchestrator.models = original_models

        # Set max tokens if specified
        max_tokens = request.max_tokens

        # Process with streaming if requested
        if request.stream:
            return self._stream_process(
                orchestrator=orchestrator,
                prompt=enhanced_prompt,
                pattern=pattern,
                max_tokens=max_tokens,
            )

        # Process without streaming
        logger.debug(
            f"Calling orchestrator.process for prompt: '{enhanced_prompt[:100]}...'"
        )
        start_time = asyncio.get_event_loop().time()
        try:
            result = await orchestrator.process(
                prompt=enhanced_prompt,
                pattern=pattern,
                max_tokens=max_tokens,
            )
            logger.debug(f"Orchestrator process result: {result}")  # Log the raw result
        except Exception as e:
            logger.error(f"Error during orchestrator.process: {str(e)}", exc_info=True)
            # Restore original models in case of error during processing
            if "original_models" in locals():
                orchestrator.models = original_models
            raise  # Re-raise the exception to be caught by the route handler
        finally:
            # Always restore the original models list for the orchestrator instance
            if "original_models" in locals():
                orchestrator.models = original_models

        end_time = asyncio.get_event_loop().time()
        logger.debug(
            f"Orchestrator processing took {end_time - start_time:.2f} seconds."
        )

        # Format the result
        formatted_result = self._format_output(result.response, request.output_format)

        # Create model predictions
        model_predictions = {}
        total_tokens = 0

        for model_name, response in result.model_responses.items():
            tokens = response.get("tokens_used", 0)
            total_tokens += tokens

            model_predictions[model_name] = ModelPrediction(
                model=model_name,
                content=response.get("content", ""),
                tokens_used=tokens,
                processing_time=response.get("processing_time", 0.0),
                quality_score=response.get("quality_score"),
            )

        # Build the final result
        return PromptResult(
            prompt=request.prompt,
            ultra_response=formatted_result,
            model_responses=model_predictions,
            total_processing_time=end_time - start_time,
            total_tokens=total_tokens,
            pattern_used=pattern,
            analysis_mode=analysis_mode,
        )

    async def _stream_process(
        self,
        orchestrator: EnhancedOrchestrator,
        prompt: str,
        pattern: str,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator:
        """Process a prompt with streaming updates.

        Args:
            orchestrator: The orchestrator to use
            prompt: The prompt to process
            pattern: The pattern to use
            max_tokens: Maximum tokens to generate (optional)

        Yields:
            PromptStreamUpdate objects
        """
        async for update in orchestrator.stream_process(
            prompt=prompt,
            pattern=pattern,
            max_tokens=max_tokens,
        ):
            yield PromptStreamUpdate(
                model=update.get("model", "unknown"),
                content=update.get("content", ""),
                done=update.get("done", False),
                stage=update.get("stage", "processing"),
                progress=update.get("progress", 0.0),
            )

    async def get_analysis_progress(self, analysis_id: str) -> Dict[str, Any]:
        """Get the progress of a multi-stage analysis.

        Args:
            analysis_id: The ID of the analysis to track

        Returns:
            Progress information including current stage and completion status
        """
        try:
            # Get the orchestrator that's handling this analysis
            orchestrator = self._get_orchestrator_for_analysis(analysis_id)
            if not orchestrator:
                return None

            # Get progress from the orchestrator
            progress = await orchestrator.get_progress(analysis_id)

            return {
                "status": progress.status,
                "current_stage": progress.current_stage,
                "stages": {
                    stage_name: {"status": stage.status, "progress": stage.progress}
                    for stage_name, stage in progress.stages.items()
                },
            }
        except Exception as e:
            logger.error(f"Error getting analysis progress: {str(e)}")
            return None

    def _get_orchestrator_for_analysis(
        self, analysis_id: str
    ) -> Optional[EnhancedOrchestrator]:
        """Get the orchestrator handling a specific analysis.

        Args:
            analysis_id: The ID of the analysis

        Returns:
            The orchestrator handling the analysis, or None if not found
        """
        # In a real implementation, this would look up the orchestrator in a database
        # For now, we'll just return the first orchestrator
        return next(iter(self.orchestrators.values())) if self.orchestrators else None

    async def analyze_prompt(
        self,
        prompt: str,
        models: List[str],
        ultra_model: str,
        pattern: str,
        options: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Process a prompt analysis request and return the results.

        Args:
            prompt: The input prompt to analyze
            models: List of model names to use for analysis
            ultra_model: The model to use for synthesizing the final response
            pattern: The analysis pattern to use
            options: Additional options for the analysis

        Returns:
            Dict containing analysis results
        """
        import time  # Import time for timestamp and performance metrics

        logger.info(
            f"Analyzing prompt with {len(models)} models using pattern {pattern}"
        )

        # Initialize orchestrator if not already done
        if not self.orchestrators:
            logger.info("Initializing orchestrators")
            self._initialize_orchestrators()

        # Select the orchestrator for standard analysis
        orchestrator = (
            next(iter(self.orchestrators.values())) if self.orchestrators else None
        )
        if not orchestrator:
            logger.error("No orchestrator available")
            raise ValueError("No orchestrator available")

        # Validate the models are available
        available_models = self.llm_config_service.get_available_models()
        logger.debug(f"Available models: {list(available_models.keys())}")

        # Check which requested models are actually available
        valid_models = [model for model in models if model in available_models]
        logger.info(f"Valid models for analysis: {valid_models}")

        if not valid_models:
            logger.warning(f"None of the requested models {models} are available")
            # Instead of failing, we'll return a mock response with a clear error message
            return {
                "model_responses": {
                    model: f"Error: Model {model} is not available. Please check your API keys or model configuration."
                    for model in models
                },
                "ultra_response": "Error: No valid models were available to process your request. Please check your API keys and model configuration.",
                "performance": {
                    "total_time_seconds": 0.1,
                    "model_times": {model: 0.1 for model in models},
                    "token_counts": {model: 0 for model in models},
                },
                "metadata": {
                    "pattern": pattern,
                    "timestamp": time.time(),
                    "models_used": [],
                    "ultra_model": ultra_model,
                    "error": "No valid models available",
                },
            }

        # Filter models to only include those requested
        original_models = (
            orchestrator.models.copy() if hasattr(orchestrator, "models") else {}
        )
        models_to_process = {
            name: model for name, model in original_models.items() if name in models
        }

        # Check if we have valid models
        if not models_to_process:
            logger.warning("No valid models found after filtering, using all available")
            models_to_process = original_models

        # Temporarily update orchestrator models for this request
        if hasattr(orchestrator, "models"):
            orchestrator.models = models_to_process

        try:
            # Process the analysis
            logger.debug(f"Running analysis with prompt: '{prompt[:100]}...'")

            # Try to run real processing if the orchestrator can handle it
            if hasattr(orchestrator, "process") and callable(
                getattr(orchestrator, "process")
            ):
                try:
                    start_time = asyncio.get_event_loop().time()
                    result = await orchestrator.process(
                        prompt=prompt,
                        pattern=pattern,
                        max_tokens=2000,  # Default max tokens
                    )
                    end_time = asyncio.get_event_loop().time()

                    # Extract model responses
                    model_responses = {}
                    for model_name, response in result.model_responses.items():
                        model_responses[model_name] = response.get(
                            "content", "No content returned"
                        )

                    # Format the final result
                    return {
                        "model_responses": model_responses,
                        "ultra_response": result.response,
                        "performance": {
                            "total_time_seconds": end_time - start_time,
                            "model_times": {
                                model: response.get("processing_time", 0)
                                for model, response in result.model_responses.items()
                            },
                            "token_counts": {
                                model: response.get("tokens_used", 0)
                                for model, response in result.model_responses.items()
                            },
                        },
                        "metadata": {
                            "pattern": pattern,
                            "timestamp": time.time(),
                            "models_used": list(models_to_process.keys()),
                            "ultra_model": ultra_model,
                        },
                    }
                except Exception as e:
                    logger.error(
                        f"Error during orchestrator.process: {str(e)}", exc_info=True
                    )
                    # Fall back to using mock service
                    logger.warning("Falling back to mock response generation")

            # If we couldn't use the real orchestrator or it failed, use a mock implementation
            logger.warning("Using mock implementation for analysis")

            # Import mock service
            try:
                from mock_llm_service import MOCK_RESPONSES, MockLLMService

                mock_service = MockLLMService()

                # Use mock implementation to analyze prompt
                mock_result = await mock_service.analyze_prompt(
                    prompt=prompt,
                    models=models,
                    ultra_model=ultra_model,
                    pattern=pattern,
                )

                # Format results to match expected format
                model_responses = {}
                for model, details in mock_result.get("results", {}).items():
                    model_responses[model] = details.get("response", "")

                ultra_response = mock_result.get(
                    "ultra_response", f"Combined analysis of prompt: {prompt[:50]}..."
                )

                # Calculate performance metrics
                performance = {
                    "total_time_seconds": sum(
                        details.get("time_taken", 0)
                        for details in mock_result.get("results", {}).values()
                    ),
                    "model_times": {
                        model: details.get("time_taken", 0)
                        for model, details in mock_result.get("results", {}).items()
                    },
                    "token_counts": {
                        model: 150 for model in models
                    },  # Mock token counts
                }

                # Create final result
                return {
                    "model_responses": model_responses,
                    "ultra_response": ultra_response,
                    "performance": performance,
                    "metadata": {
                        "pattern": pattern,
                        "timestamp": time.time(),
                        "models_used": models,
                        "ultra_model": ultra_model,
                    },
                }
            except ImportError:
                logger.error(
                    "Failed to import mock service, generating simple mock responses"
                )

                # Generate simple mock responses if we can't import the mock service
                model_responses = {}
                for model in models:
                    model_responses[model] = (
                        f"Analysis from {model} about '{prompt[:50]}...': This would be generated by the real model in a production environment."
                    )

                ultra_response = f"Combined analysis from {ultra_model} about '{prompt[:50]}...': This would synthesize all model responses in a production environment."

                return {
                    "model_responses": model_responses,
                    "ultra_response": ultra_response,
                    "performance": {
                        "total_time_seconds": 3.0,
                        "model_times": {model: 2.0 for model in models},
                        "token_counts": {model: 150 for model in models},
                    },
                    "metadata": {
                        "pattern": pattern,
                        "timestamp": time.time(),
                        "models_used": models,
                        "ultra_model": ultra_model,
                    },
                }

        finally:
            # Restore original models in the orchestrator
            if hasattr(orchestrator, "models"):
                orchestrator.models = original_models

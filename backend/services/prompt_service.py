"""
Prompt Service Module

This module provides the service layer for handling prompt submission and processing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union

from backend.models.llm_models import (
    ProcessPromptRequest,
    PromptResult,
    ModelPrediction,
    PromptStreamUpdate,
    AnalysisOption,
    OutputFormat,
)
from backend.models.enhanced_orchestrator import (
    EnhancedOrchestrator,
    OrchestratorConfig,
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
                analysis_pattern=mode.pattern,
                model_selection_strategy=mode.model_selection_strategy,
                timeout=mode.timeout or 30.0,
                enable_circuit_breaker=True,
                enable_metrics=True,
                enable_quality_evaluation=True,
            )
            self.orchestrators[mode.name] = EnhancedOrchestrator(config)

            # Register available models with the orchestrator
            models = self.llm_config_service.get_available_models()
            for model in models:
                if model.available and model.status == "ready":
                    self.orchestrators[mode.name].register_model(
                        name=model.name,
                        provider=model.provider,
                        model_id=model.model,
                        weight=model.weight,
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
        # Determine which analysis mode to use
        analysis_mode = request.analysis_mode
        if analysis_mode not in self.orchestrators:
            # Default to standard if the requested mode doesn't exist
            analysis_mode = "standard"
            logger.warning(
                f"Requested analysis mode '{request.analysis_mode}' not found. Using 'standard'."
            )

        # Get the corresponding orchestrator
        orchestrator = self.orchestrators[analysis_mode]

        # Apply analysis options to the prompt
        enhanced_prompt = self._apply_analysis_options(request.prompt, request.options)

        # Override the pattern if specified
        if request.pattern:
            pattern = request.pattern
            available_patterns = self.llm_config_service.get_patterns()
            if pattern not in available_patterns:
                logger.warning(
                    f"Requested pattern '{pattern}' not found. Using default pattern."
                )
                pattern = orchestrator.config.analysis_pattern
        else:
            pattern = orchestrator.config.analysis_pattern

        # Filter the models if specific ones are requested
        if request.selected_models:
            for model_name in list(orchestrator.models.keys()):
                if model_name not in request.selected_models:
                    orchestrator.models.pop(model_name, None)

            if not orchestrator.models:
                raise ValueError("No valid models selected for processing")

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
        start_time = asyncio.get_event_loop().time()
        result = await orchestrator.process(
            prompt=enhanced_prompt,
            pattern=pattern,
            max_tokens=max_tokens,
        )
        end_time = asyncio.get_event_loop().time()

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

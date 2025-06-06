"""
Fix for the analysis model configuration.

This module provides a function to fix the analysis model configuration
in the ModularOrchestrator class.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def configure_analysis_options(
    options: Dict[str, Any],
    lead_model_adapter: Any,
    lead_model_name: str,
    responses: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Configure analysis options with proper model assignment.

    Args:
        options: Current options dictionary
        lead_model_adapter: Adapter for the lead model
        lead_model_name: Name of the lead model
        responses: List of model responses

    Returns:
        Updated options with analysis model properly configured
    """
    # Create a copy of options
    updated_options = options.copy() if options else {}

    # Ensure the analysis model is set properly
    if not updated_options.get("analysis_model"):
        updated_options["analysis_model"] = lead_model_adapter
        logger.info(f"Using {lead_model_name} as the analysis model")

    # Add lead model name
    updated_options["lead_model_name"] = lead_model_name

    # Log the model assignment
    logger.info(f"Analysis configured with model: {lead_model_name}")

    return updated_options


def patch_modular_orchestrator():
    """
    Apply a monkey patch to the ModularOrchestrator to fix the analysis model configuration.

    This should be called before creating any ModularOrchestrator instances.
    """
    try:
        from src.simple_core.modular_orchestrator import ModularOrchestrator

        # Save the original method
        original_perform_analysis = ModularOrchestrator._perform_analysis

        # Define the patched method
        async def patched_perform_analysis(
            self,
            prompt: str,
            responses: List[Any],
            analysis_type: str,
            lead_model: tuple,
            request: Dict[str, Any],
        ) -> Dict[str, Any]:
            """Patched version of _perform_analysis that ensures the analysis model is set."""
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

            # Configure analysis options with our enhanced function
            options = {}

            # Add any additional options from the request
            if request.get("options") and isinstance(request["options"], dict):
                options.update(request["options"])

            # Enhanced configuration that ensures the analysis model is set
            options = configure_analysis_options(
                options,
                lead_model[1],  # Adapter
                lead_model[0].name,  # Model name
                response_dicts,
            )

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

        # Apply the patch
        ModularOrchestrator._perform_analysis = patched_perform_analysis
        logger.info("Successfully patched ModularOrchestrator._perform_analysis")

        return True
    except Exception as e:
        logger.error(f"Failed to patch ModularOrchestrator: {e}")
        return False

"""
SimpleOrchestrator module for a streamlined orchestration experience.

This module provides a simple implementation of the BaseOrchestrator that follows
a basic workflow: collecting responses from multiple providers, analyzing the results,
and synthesizing a final response.
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union, Tuple

from src.orchestration.base_orchestrator import BaseOrchestrator
from src.orchestration.config import LLMProvider


logger = logging.getLogger(__name__)


@dataclass
class OrchestratorResponse:
    """Standard response format for the orchestrator."""
    initial_responses: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    synthesis: Dict[str, Any]
    metadata: Dict[str, Any]
    error: Optional[str] = None


class SimpleOrchestrator(BaseOrchestrator):
    """
    Simple orchestrator that implements a basic workflow:
    1. Collect responses from multiple providers
    2. Analyze the results
    3. Synthesize a final response

    This implementation uses a designated lead provider for analysis and synthesis.
    """

    def __init__(
        self,
        max_retries: int = 3,
        parallel_requests: bool = True,
        timeout_seconds: int = 30,
        analysis_type: str = "comparative"
    ):
        """
        Initialize the simple orchestrator.

        Args:
            max_retries: Maximum number of retries for failed requests
            parallel_requests: Whether to process LLM requests in parallel
            timeout_seconds: Timeout for LLM requests in seconds
            analysis_type: Type of analysis to perform (comparative or factual)
        """
        super().__init__(
            max_retries=max_retries,
            parallel_requests=parallel_requests,
            timeout_seconds=timeout_seconds
        )
        self.analysis_type = analysis_type
        self.lead_provider_id: Optional[str] = None
        self.logger = logging.getLogger("orchestrator.simple")

    def set_lead_provider(self, provider_id: str) -> bool:
        """
        Set the lead provider for analysis and synthesis.

        Args:
            provider_id: The provider ID to use as lead

        Returns:
            True if successful, False if provider not registered
        """
        if provider_id not in self.providers:
            self.logger.warning(f"Cannot set lead provider '{provider_id}': not registered")
            return False

        self.lead_provider_id = provider_id
        self.logger.info(f"Set lead provider to '{provider_id}'")
        return True

    def get_lead_provider_id(self) -> Optional[str]:
        """
        Get the current lead provider ID.

        Returns:
            The lead provider ID or None if not set
        """
        return self.lead_provider_id

    async def _analyze_responses(
        self,
        prompt: str,
        responses: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze the responses from multiple providers.

        Args:
            prompt: The original prompt
            responses: Dictionary of provider responses

        Returns:
            Analysis results
        """
        # Skip analysis if there's only one or zero responses
        successful_responses = {
            provider_id: info for provider_id, info in responses.items()
            if info.get("success", False)
        }

        if len(successful_responses) <= 1:
            self.logger.info("Only one successful response, skipping analysis")
            return {
                "type": self.analysis_type,
                "summary": "No analysis performed (insufficient successful responses)",
                "combined_summary": "Only one or fewer models provided successful responses, so no comparative analysis is available."
            }

        # Determine which provider to use for analysis
        analyzer_id = self.lead_provider_id
        if not analyzer_id or analyzer_id not in successful_responses:
            # Fall back to the first successful provider
            analyzer_id = list(successful_responses.keys())[0]
            self.logger.info(f"Using '{analyzer_id}' as fallback analyzer")

        # Create analysis prompt
        if self.analysis_type == "comparative":
            analysis_prompt = "Compare these responses to the following prompt:\n\n"
            analysis_prompt += f"PROMPT: {prompt}\n\n"

            for i, (provider_id, info) in enumerate(successful_responses.items(), 1):
                response_text = info.get("response", "No response")
                analysis_prompt += f"RESPONSE {i} ({provider_id}):\n{response_text}\n\n"

            analysis_prompt += "Please provide a detailed comparison of these responses, highlighting key differences, agreements, and which provides the most helpful information."
        else:
            # Factual analysis
            analysis_prompt = "Analyze the factual accuracy of these responses to the following prompt:\n\n"
            analysis_prompt += f"PROMPT: {prompt}\n\n"

            for i, (provider_id, info) in enumerate(successful_responses.items(), 1):
                response_text = info.get("response", "No response")
                analysis_prompt += f"RESPONSE {i} ({provider_id}):\n{response_text}\n\n"

            analysis_prompt += "Please analyze these responses for factual accuracy, identifying any errors or misleading statements."

        # Send analysis request to the analyzer provider
        try:
            analysis_response, metadata = await self.send_request_to_provider(
                analyzer_id, analysis_prompt
            )

            return {
                "type": self.analysis_type,
                "analyzer_id": analyzer_id,
                "combined_summary": analysis_response,
                "metadata": metadata
            }
        except Exception as e:
            self.logger.error(f"Error during analysis with provider '{analyzer_id}': {e}")

            return {
                "type": self.analysis_type,
                "error": str(e),
                "combined_summary": f"Analysis failed: {str(e)}",
                "analyzer_id": analyzer_id
            }

    async def _synthesize_response(
        self,
        prompt: str,
        responses: Dict[str, Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize a final response using the lead provider.

        Args:
            prompt: The original prompt
            responses: Dictionary of provider responses
            analysis: Analysis results

        Returns:
            Synthesis results
        """
        # Determine which provider to use for synthesis
        synthesizer_id = self.lead_provider_id
        if not synthesizer_id or synthesizer_id not in self.providers:
            # Fall back to the first provider
            synthesizer_id = list(self.providers.keys())[0]
            self.logger.info(f"Using '{synthesizer_id}' as fallback synthesizer")

        # Create synthesis prompt
        synthesis_prompt = f"Based on the following analysis of multiple responses to this prompt:\n\n"
        synthesis_prompt += f"PROMPT: {prompt}\n\n"
        synthesis_prompt += f"ANALYSIS: {analysis.get('combined_summary', 'No analysis available')}\n\n"
        synthesis_prompt += "Please provide a comprehensive response that synthesizes the best information from all sources."

        # Send synthesis request to the synthesizer provider
        try:
            synthesis_response, metadata = await self.send_request_to_provider(
                synthesizer_id, synthesis_prompt
            )

            return {
                "synthesizer_id": synthesizer_id,
                "response": synthesis_response,
                "metadata": metadata
            }
        except Exception as e:
            self.logger.error(f"Error during synthesis with provider '{synthesizer_id}': {e}")

            return {
                "synthesizer_id": synthesizer_id,
                "error": str(e),
                "response": f"Synthesis failed: {str(e)}"
            }

    async def process(
        self,
        prompt: str,
        provider_ids: Optional[List[str]] = None,
        **options
    ) -> Dict[str, Any]:
        """
        Process a prompt using the simple orchestration workflow.

        Args:
            prompt: The prompt to process
            provider_ids: Optional list of provider IDs to use (defaults to all registered)
            **options: Additional processing options

        Returns:
            OrchestratorResponse with initial responses, analysis, and synthesis
        """
        start_time = asyncio.get_event_loop().time()

        # Get provider IDs to use
        if provider_ids is None:
            provider_ids = list(self.providers.keys())

        # Validate provider IDs
        invalid_providers = [pid for pid in provider_ids if pid not in self.providers]
        if invalid_providers:
            self.logger.warning(f"Ignoring invalid providers: {', '.join(invalid_providers)}")
            provider_ids = [pid for pid in provider_ids if pid in self.providers]

        if not provider_ids:
            error_msg = "No valid providers specified"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "initial_responses": [],
                "analysis_results": {
                    "type": self.analysis_type,
                    "summary": "No analysis performed (no valid providers)"
                },
                "synthesis": {
                    "response": "No synthesis available (no valid providers)"
                },
                "metadata": {
                    "processing_time": asyncio.get_event_loop().time() - start_time,
                    "providers_requested": len(provider_ids) if provider_ids else 0,
                    "providers_successful": 0
                }
            }

        # Step 1: Get responses from all providers
        self.logger.info(f"Processing prompt with {len(provider_ids)} providers")
        provider_responses = await self.process_with_providers(prompt, provider_ids, **options)

        # Count successful responses
        successful_responses = sum(
            1 for info in provider_responses.values() if info.get("success", False)
        )

        # If no successful responses, return error
        if successful_responses == 0:
            error_msg = "No successful responses from any provider"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "initial_responses": [
                    {
                        "provider_id": provider_id,
                        "success": info.get("success", False),
                        "error": info.get("error", "Unknown error"),
                        "error_type": info.get("error_type", "Unknown")
                    }
                    for provider_id, info in provider_responses.items()
                ],
                "analysis_results": {
                    "type": self.analysis_type,
                    "summary": "No analysis performed (no successful responses)"
                },
                "synthesis": {
                    "response": "No synthesis available (no successful responses)"
                },
                "metadata": {
                    "processing_time": asyncio.get_event_loop().time() - start_time,
                    "providers_requested": len(provider_ids),
                    "providers_successful": 0
                }
            }

        # Step 2: Analyze responses
        analysis_results = await self._analyze_responses(prompt, provider_responses)

        # Step 3: Synthesize response
        synthesis = await self._synthesize_response(prompt, provider_responses, analysis_results)

        # Return consolidated results
        return {
            "initial_responses": [
                {
                    "provider_id": provider_id,
                    "success": info.get("success", False),
                    "response": info.get("response", "") if info.get("success", False) else None,
                    "error": info.get("error", None) if not info.get("success", False) else None,
                    "metadata": info.get("metadata", {}) if info.get("success", False) else None
                }
                for provider_id, info in provider_responses.items()
            ],
            "analysis_results": analysis_results,
            "synthesis": synthesis,
            "metadata": {
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "providers_requested": len(provider_ids),
                "providers_successful": successful_responses,
                "analysis_type": self.analysis_type
            }
        }
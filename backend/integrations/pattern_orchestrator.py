"""
Pattern Orchestrator for the Ultra backend.

This module provides a service for orchestrating multiple LLM requests
according to different analysis patterns.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger("pattern_orchestrator")


class PatternOrchestrator:
    """Service for orchestrating multiple LLM requests with analysis patterns"""

    def __init__(
        self,
        models: Optional[List[str]] = None,
        ultra_model: Optional[str] = None,
        pattern: str = "comprehensive_analysis",
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the pattern orchestrator

        Args:
            models: List of models to use
            ultra_model: Ultra model to use
            pattern: Analysis pattern
            options: Additional options
        """
        self.models = models or []
        self.ultra_model = ultra_model
        self.pattern = pattern
        self.options = options or {}
        self.timeout = options.get("timeout", 60) if options else 60

        logger.info(f"Initialized PatternOrchestrator with pattern: {pattern}")

    async def process(self, prompt: str) -> Dict[str, Any]:
        """
        Process a prompt with multiple models according to the pattern

        Args:
            prompt: Prompt to analyze

        Returns:
            Analysis results
        """
        start_time = time.time()
        logger.info(f"Processing prompt with pattern: {self.pattern}")

        # Simulate model responses
        model_responses = {}
        model_times = {}
        token_counts = {}

        # Process each model with simulated response times
        tasks = []
        for model in self.models:
            tasks.append(self._process_with_model(prompt, model))

        # Run model tasks in parallel
        results = await asyncio.gather(*tasks)

        # Extract results
        for model, response, processing_time, tokens in results:
            model_responses[model] = response
            model_times[model] = processing_time
            token_counts[model] = tokens

        # Process with ultra model
        ultra_response = await self._process_with_ultra_model(prompt, model_responses)

        # Calculate total processing time
        end_time = time.time()
        processing_time = end_time - start_time

        # Create result
        result = {
            "status": "success",
            "model_responses": model_responses,
            "ultra_response": ultra_response,
            "pattern": self.pattern,
            "model_times": model_times,
            "token_counts": token_counts,
            "total_time": processing_time,
            "options_used": self.options
        }

        return result

    async def _process_with_model(self, prompt: str, model: str) -> tuple:
        """
        Process a prompt with a single model

        Args:
            prompt: Prompt to analyze
            model: Model to use

        Returns:
            Tuple of (model, response, processing_time, token_counts)
        """
        # Simulate model processing time (normally this would call the model API)
        model_start_time = time.time()

        # Different models have different simulated response times
        if "gpt" in model:
            sleep_time = 1.0
        elif "claude" in model:
            sleep_time = 1.5
        elif "gemini" in model:
            sleep_time = 1.8
        else:
            sleep_time = 2.0

        await asyncio.sleep(sleep_time)

        # Create a simulated response
        response = f"Analysis from {model}: This prompt discusses {prompt[:30]}..."

        # Calculate processing time
        model_end_time = time.time()
        processing_time = model_end_time - model_start_time

        # Simulate token counts
        token_counts = {
            "prompt_tokens": len(prompt.split()) * 4,
            "completion_tokens": len(response.split()) * 4,
            "total_tokens": (len(prompt.split()) + len(response.split())) * 4
        }

        logger.info(f"Model {model} processed prompt in {processing_time:.2f} seconds")
        return model, response, processing_time, token_counts

    async def _process_with_ultra_model(
        self,
        prompt: str,
        model_responses: Dict[str, str]
    ) -> str:
        """
        Process all model responses with the ultra model

        Args:
            prompt: Original prompt
            model_responses: Responses from individual models

        Returns:
            Ultra model response
        """
        # Simulate ultra model processing (combine individual responses)
        await asyncio.sleep(2.0)

        # Create a simulated ultra response
        ultra_response = f"""# {self.pattern.replace('_', ' ').title()}

## Summary
This analysis combines insights from multiple models about: {prompt[:100]}...

## Model Insights
"""

        # Add individual model insights
        for model, response in model_responses.items():
            ultra_response += f"\n### {model.upper()}\n{response[:200]}...\n"

        # Add conclusion based on pattern
        if "comparative" in self.pattern:
            ultra_response += "\n## Comparison\nThe models demonstrate both similarities and differences in their analyses."
        elif "comprehensive" in self.pattern:
            ultra_response += "\n## Comprehensive Findings\nTaking all models into account, a thorough understanding emerges."
        elif "critical" in self.pattern:
            ultra_response += "\n## Critical Analysis\nEvaluating the strengths and weaknesses of each approach."
        else:
            ultra_response += "\n## Conclusion\nThe combined analysis provides valuable insights."

        logger.info(f"Ultra model processed responses with pattern: {self.pattern}")
        return ultra_response
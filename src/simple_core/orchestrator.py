"""
Orchestrator module for Simple Core.

This module provides a streamlined orchestrator for coordinating LLM requests
with minimal complexity.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union

from src.simple_core.adapter import Adapter
from src.simple_core.config import Config, ModelDefinition


class Orchestrator:
    """
    Simple orchestrator for coordinating LLM requests.

    This minimal implementation provides a streamlined path from request to response
    with built-in parallel execution and error handling.
    """

    def __init__(self, config: Config, adapters: Dict[str, Adapter]):
        """
        Initialize the orchestrator.

        Args:
            config: Configuration for the orchestrator
            adapters: Dictionary mapping model names to adapters
        """
        self.config = config
        self.adapters = adapters
        self.logger = logging.getLogger("simple_core.orchestrator")

        # Validate that we have adapters for all configured models
        for model in config.models:
            if model.name not in adapters:
                self.logger.warning(f"No adapter found for model {model.name}")

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request with configured models.

        Args:
            request: Dictionary containing prompt and options

        Returns:
            Dictionary containing results and metadata
        """
        start_time = time.time()
        prompt = request.get("prompt", "")
        options = request.get("options", {})
        models = self._get_models_for_request(request)

        if not prompt:
            return self._create_error_response("Empty prompt provided")

        if not models:
            return self._create_error_response("No valid models available")

        try:
            # Process request with all specified models
            if self.config.parallel and len(models) > 1:
                # Process in parallel
                tasks = [
                    self._process_with_model(model.name, prompt, options)
                    for model in models
                ]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                model_responses = {
                    models[i].name: self._handle_response(models[i].name, responses[i])
                    for i in range(len(models))
                }
            else:
                # Process sequentially
                model_responses = {}
                for model in models:
                    result = await self._process_with_model(model.name, prompt, options)
                    model_responses[model.name] = self._handle_response(
                        model.name, result
                    )

            # Select primary response
            primary_response = self._select_primary_response(models, model_responses)

            # Build final response
            duration = time.time() - start_time
            response = {
                "content": primary_response.get("content", ""),
                "model_responses": model_responses,
                "metadata": {
                    "time": duration,
                    "models_used": [model.name for model in models],
                    "successful_models": [
                        name
                        for name, resp in model_responses.items()
                        if "error" not in resp
                    ],
                    "primary_model": self._get_primary_model_name(
                        models, model_responses
                    ),
                },
            }

            return response

        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            return self._create_error_response(str(e))

    async def _process_with_model(
        self, model_name: str, prompt: str, options: Dict[str, Any]
    ) -> Union[str, Exception]:
        """Process a prompt with a specific model."""
        adapter = self.adapters.get(model_name)
        if not adapter:
            return Exception(f"No adapter found for model {model_name}")

        try:
            # Apply retry logic
            retries = self.config.retry_count
            last_error = None

            for attempt in range(retries):
                try:
                    return await adapter.generate(prompt, options)
                except Exception as e:
                    last_error = e
                    self.logger.warning(
                        f"Attempt {attempt + 1}/{retries} failed for {model_name}: {str(e)}"
                    )
                    if attempt < retries - 1:
                        # Wait before retrying (with exponential backoff)
                        await asyncio.sleep(2**attempt)

            # If we get here, all retries failed
            return last_error

        except Exception as e:
            self.logger.error(f"Error processing with {model_name}: {str(e)}")
            return e

    def _handle_response(
        self, model_name: str, response: Union[str, Exception]
    ) -> Dict[str, Any]:
        """Convert raw response or exception to a structured response."""
        if isinstance(response, Exception):
            return {"error": str(response), "content": None}
        return {"content": response}

    def _select_primary_response(
        self, models: List[ModelDefinition], responses: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select the primary response based on model priority and success."""
        # First try to get response from highest priority model
        for model in models:
            response = responses.get(model.name, {})
            if "error" not in response and response.get("content"):
                return response

        # If all failed, return the first response (even if it's an error)
        if responses:
            return next(iter(responses.values()))

        return {"error": "No responses available", "content": None}

    def _get_primary_model_name(
        self, models: List[ModelDefinition], responses: Dict[str, Dict[str, Any]]
    ) -> Optional[str]:
        """Get the name of the model used for the primary response."""
        for model in models:
            if model.name in responses and "error" not in responses[model.name]:
                return model.name
        return None

    def _get_models_for_request(self, request: Dict[str, Any]) -> List[ModelDefinition]:
        """Get the models to use for this request."""
        # Check if specific models are requested
        requested_models = request.get("models", [])
        if requested_models:
            # Filter to only include models that are configured
            models = [
                model
                for model in self.config.models
                if model.name in requested_models and model.name in self.adapters
            ]
            # Sort by priority
            return sorted(models, key=lambda m: m.priority, reverse=True)

        # Otherwise use all available models sorted by priority
        return [
            model
            for model in self.config.get_models_by_priority()
            if model.name in self.adapters
        ]

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create a response object for errors."""
        return {
            "content": "",
            "model_responses": {},
            "metadata": {
                "time": 0,
                "models_used": [],
                "successful_models": [],
                "primary_model": None,
                "error": error_message,
            },
        }

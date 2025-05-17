"""
Simple mock adapter for Docker-based testing.

This module provides a simplified mock adapter that works with the
simplified orchestrator in a Docker environment.
"""

import asyncio
import logging
import os
import random
import time

from src.adapters.mock_adapter import MockAdapter

logger = logging.getLogger(__name__)


class SimpleMockAdapter:
    """
    Simple mock adapter for Docker testing.

    This adapter provides a synchronous interface to the mock adapter
    for use with the simplified orchestrator.
    """

    def __init__(self, model_name="simple-mock"):
        """
        Initialize the simple mock adapter.

        Args:
            model_name: Name to use for this mock model
        """
        from src.orchestration.config import LLMProvider, ModelConfig

        # Create a model config for the mock adapter
        model_config = ModelConfig(
            provider=LLMProvider.MOCK,
            model_id=model_name.split("-")[-1],
            temperature=0.7,
            max_tokens=1000,
        )

        # Create async mock adapter
        self.async_adapter = MockAdapter(model_config)
        self.provider = "mock"

    def generate(self, prompt, **kwargs):
        """
        Generate a response synchronously.

        Args:
            prompt: The prompt to respond to
            **kwargs: Additional parameters

        Returns:
            A mock response string
        """
        # Create a new event loop for the async call
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                self.async_adapter.generate(prompt, **kwargs)
            )
        finally:
            loop.close()


def create_mock_adapter(model_name="mock-llm"):
    """
    Create a simple mock adapter instance.

    Args:
        model_name: Name to use for this mock model

    Returns:
        A SimpleMockAdapter instance
    """
    adapter = SimpleMockAdapter(model_name)
    return adapter

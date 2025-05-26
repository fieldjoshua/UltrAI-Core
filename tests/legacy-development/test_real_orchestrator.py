#!/usr/bin/env python3
"""
Test script for the MultiLLMOrchestrator with real LLM adapters.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

# Add the project root to PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.models.llm_adapter import LLMAdapter, create_adapter_async
from src.orchestrator import MultiLLMOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def initialize_adapters() -> Dict[str, LLMAdapter]:
    """
    Initialize LLM adapters based on available API keys in environment.

    Returns:
        Dictionary mapping model names to adapter instances
    """
    adapters = {}

    # Check for OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            adapter = await create_adapter_async("openai", openai_key, model="gpt-4")
            adapters["openai_gpt4"] = adapter
            logger.info("Initialized OpenAI GPT-4 adapter")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI adapter: {e}")

    # Check for Anthropic
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            adapter = await create_adapter_async(
                "anthropic", anthropic_key, model="claude-3-opus-20240229"
            )
            adapters["anthropic_claude"] = adapter
            logger.info("Initialized Anthropic Claude adapter")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic adapter: {e}")

    # Check for Google/Gemini
    google_key = os.environ.get("GOOGLE_API_KEY")
    if google_key:
        try:
            adapter = await create_adapter_async(
                "gemini", google_key, model="gemini-pro"
            )
            adapters["google_gemini"] = adapter
            logger.info("Initialized Google Gemini adapter")
        except Exception as e:
            logger.error(f"Failed to initialize Google adapter: {e}")

    # If no real adapters are available, create mock adapters
    if not adapters:
        logger.warning("No API keys found, using mock adapters")

        # Create a wrapper class to adapt the LLMAdapter to the orchestrator's expected interface
        class MockClientWrapper:
            def __init__(self, adapter: LLMAdapter):
                self.adapter = adapter
                self.name = adapter.name

            async def generate(self, prompt: str) -> str:
                return await self.adapter.generate(prompt)

            def __class__(self):
                return type(self).__name__

        # Create a mock OpenAI adapter as a fallback
        try:
            mock_adapter = await create_adapter_async(
                "openai", "sk-mock-key", model="gpt-4"
            )
            adapters["mock_openai"] = MockClientWrapper(mock_adapter)
            logger.info("Initialized mock OpenAI adapter")

            mock_anthropic = await create_adapter_async(
                "anthropic", "sk-ant-mock-key", model="claude-3-opus-20240229"
            )
            adapters["mock_claude"] = MockClientWrapper(mock_anthropic)
            logger.info("Initialized mock Claude adapter")
        except Exception as e:
            logger.error(f"Failed to initialize mock adapters: {e}")

    return adapters


async def test_multi_llm_orchestrator():
    """Test the MultiLLMOrchestrator with real LLM providers."""

    logger.info("Creating MultiLLMOrchestrator with real LLM providers...")

    # Initialize the orchestrator
    orchestrator = MultiLLMOrchestrator(cache_enabled=True, max_retries=2)

    # Initialize and register LLM adapters
    adapters = await initialize_adapters()
    if not adapters:
        logger.error("No adapters could be initialized. Please check your API keys.")
        return False

    # Register adapters with the orchestrator
    for name, adapter in adapters.items():
        orchestrator.register_model(name, adapter)
        logger.info(f"Registered adapter: {name}")

    # Create a test prompt
    prompt = (
        "Explain the benefits of a microservices architecture over monolithic design"
    )

    logger.info(f"Processing prompt with available models: {prompt}")

    # Process the prompt with all registered models
    response = await orchestrator.process_responses(
        prompt=prompt,
        stages=["initial", "meta", "synthesis"],
        models=None,  # Use all registered models
    )

    # Check if the response was successful
    if response.get("status") != "success":
        logger.error(
            f"Error processing prompt: {response.get('error', 'Unknown error')}"
        )
        return False

    # Format and display results
    logger.info("\nResults:")
    logger.info(f"Status: {response['status']}")
    logger.info(f"Timestamp: {response['timestamp']}")

    # Show initial responses
    logger.info("\nInitial Responses:")
    for resp_json in response.get("initial_responses", []):
        resp = json.loads(resp_json)
        logger.info(f"- Model: {resp.get('model_name')}")
        logger.info(f"  Stage: {resp.get('stage')}")
        logger.info(f"  Quality score: {resp.get('quality_scores', {}).get('average')}")

    # Show meta responses if available
    meta_responses = response.get("meta_responses", [])
    if meta_responses:
        logger.info("\nMeta Responses:")
        for resp_json in meta_responses:
            resp = json.loads(resp_json)
            logger.info(f"- Model: {resp.get('model_name')}")
            logger.info(f"  Stage: {resp.get('stage')}")

    # Show final synthesis if available
    final_synthesis = response.get("final_synthesis")
    if final_synthesis:
        logger.info("\nFinal Synthesis:")
        synth = json.loads(final_synthesis)
        logger.info(f"- Model: {synth.get('model_name')}")
        logger.info(f"  Stage: {synth.get('stage')}")

    # Save the result to a file for inspection
    output_file = os.path.join(project_root, "real_orchestrator_result.json")
    with open(output_file, "w") as f:
        json.dump(response, f, indent=2)

    logger.info(f"Results saved to {output_file}")
    return True


def main():
    """Main function to run the test."""
    logger.info("Starting MultiLLMOrchestrator test with real LLM providers...")

    # Run the async test
    try:
        success = asyncio.run(test_multi_llm_orchestrator())
        if success:
            logger.info("Test completed successfully!")
        else:
            logger.error("Test failed. See logs for details.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

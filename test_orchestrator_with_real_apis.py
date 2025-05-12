#!/usr/bin/env python3
"""
Test script for the MultiLLMOrchestrator using real API keys.

This script demonstrates how to set up the orchestrator with real LLM providers.
It requires API keys to be set in environment variables:
- OPENAI_API_KEY for OpenAI
- ANTHROPIC_API_KEY for Anthropic/Claude
- GOOGLE_API_KEY for Google/Gemini

Usage:
    Export your API keys and run:
    python3 test_orchestrator_with_real_apis.py
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

# Add the project root to PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import necessary components
from src.orchestrator import MultiLLMOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleClientAdapter:
    """
    A simple adapter to match the interface expected by the orchestrator.
    This wraps provider-specific clients to implement the generate method.
    """

    def __init__(self, name, provider, model_id, api_key):
        self.name = name
        self.provider = provider
        self.model_id = model_id
        self.api_key = api_key

        # Initialize the appropriate client based on the provider
        if provider == "openai":
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=api_key)
        elif provider == "anthropic":
            from anthropic import AsyncAnthropic

            self.client = AsyncAnthropic(api_key=api_key)
        elif provider == "google":
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_id)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def generate(self, prompt: str) -> str:
        """Generate a response using the appropriate LLM provider."""
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                )
                return response.choices[0].message.content

            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model_id,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                )
                return response.content[0].text

            elif self.provider == "google":
                response = await self.model.generate_content_async(prompt)
                return response.text

        except Exception as e:
            logger.error(f"Error with {self.provider} {self.model_id}: {str(e)}")
            return f"Error generating response with {self.provider} {self.model_id}: {str(e)}"

    def __class__(self):
        """Return the name of the class for identification."""
        return f"{self.provider}_{self.model_id}"


async def test_orchestrator():
    """Test the orchestrator with real API keys."""

    # Check for required API keys
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")

    if not any([openai_key, anthropic_key, google_key]):
        logger.error(
            "No API keys found. Please set at least one of OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY."
        )
        sys.exit(1)

    # Initialize the orchestrator
    orchestrator = MultiLLMOrchestrator(cache_enabled=True, max_retries=2)

    # Register models based on available API keys
    if openai_key:
        logger.info("Registering OpenAI GPT-4o model")
        gpt4o_client = SimpleClientAdapter("GPT-4o", "openai", "gpt-4o", openai_key)
        orchestrator.register_model("gpt4o", gpt4o_client, weight=1.0)

    if anthropic_key:
        logger.info("Registering Anthropic Claude-3 Opus model")
        claude_client = SimpleClientAdapter(
            "Claude-3-Opus", "anthropic", "claude-3-opus-20240229", anthropic_key
        )
        orchestrator.register_model("claude3opus", claude_client, weight=1.0)

    if google_key:
        logger.info("Registering Google Gemini Pro model")
        gemini_client = SimpleClientAdapter(
            "Gemini-Pro", "google", "gemini-1.5-pro-latest", google_key
        )
        orchestrator.register_model("gemini15pro", gemini_client, weight=0.9)

    # Create a test prompt
    prompt = "Explain the benefits of a multi-LLM orchestration approach compared to using a single LLM provider"

    logger.info(f"Processing prompt with orchestrator: {prompt}")

    # Process the prompt with all registered models
    response = await orchestrator.process_responses(
        prompt=prompt,
        stages=["initial", "meta", "synthesis"],  # Use all stages
        models=None,  # Use all registered models
    )

    # Format and display results
    logger.info("\nResults:")
    logger.info(f"Status: {response['status']}")
    logger.info(f"Timestamp: {response['timestamp']}")

    # Save the detailed response to a file
    output_file = os.path.join(project_root, "orchestrator_result.json")
    with open(output_file, "w") as f:
        json.dump(response, f, indent=2)

    logger.info(f"Detailed results saved to: {output_file}")

    # Show summary of initial responses
    logger.info("\nInitial Responses:")
    for resp_json in response.get("initial_responses", []):
        try:
            resp = json.loads(resp_json)
            logger.info(f"- Model: {resp.get('model_name')}")
        except:
            logger.error(f"Could not parse response: {resp_json[:100]}...")

    # Show final synthesis if available
    if response.get("final_synthesis"):
        logger.info("\nFinal Synthesis Summary:")
        try:
            synth = json.loads(response["final_synthesis"])
            logger.info(f"- Model: {synth.get('model_name')}")

            # Also save the final synthesis content to a separate file
            synthesis_file = os.path.join(project_root, "synthesis_result.txt")
            with open(synthesis_file, "w") as f:
                f.write(synth.get("content", "No content available"))

            logger.info(f"Final synthesis content saved to: {synthesis_file}")
        except:
            logger.error("Could not parse final synthesis")

    return response


def main():
    """Main function to run the test."""
    logger.info("Starting MultiLLMOrchestrator test with real API keys")

    # Run the async test
    try:
        response = asyncio.run(test_orchestrator())
        logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

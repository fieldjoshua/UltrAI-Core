"""
Example script demonstrating the use of the UltraAI orchestration system.

This script shows how to initialize different orchestrator types, register providers,
and process prompts using various orchestration strategies.
"""

import asyncio
import logging
import os
from typing import Any, Dict

from src.orchestration import (
    AdaptiveOrchestrator,
    OrchestrationStrategy,
    ParallelOrchestrator,
    SimpleOrchestrator,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("orchestrator_example")


async def register_providers(orchestrator):
    """Register LLM providers with the orchestrator."""
    # Register OpenAI provider if API key is available
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        await orchestrator.register_provider(
            provider_id="openai-gpt4o",
            provider_type="openai",
            api_key=openai_api_key,
            model="gpt-4o",
        )
        logger.info("Registered OpenAI GPT-4o provider")

    # Register Anthropic provider if API key is available
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        await orchestrator.register_provider(
            provider_id="anthropic-claude",
            provider_type="anthropic",
            api_key=anthropic_api_key,
            model="claude-3-opus-20240229",
        )
        logger.info("Registered Anthropic Claude-3 Opus provider")

    # Register mock provider for testing
    await orchestrator.register_provider(
        provider_id="mock-llm", provider_type="mock", model="mock-model"
    )
    logger.info("Registered Mock LLM provider")

    # List all registered providers
    providers = orchestrator.get_registered_providers()
    logger.info(f"Registered providers: {providers}")


async def simple_orchestration_example():
    """Example demonstrating the SimpleOrchestrator."""
    logger.info("=== SimpleOrchestrator Example ===")

    # Initialize SimpleOrchestrator
    orchestrator = SimpleOrchestrator(
        max_retries=2, parallel_requests=True, analysis_type="comparative"
    )

    # Register providers
    await register_providers(orchestrator)

    # Set lead provider if we have OpenAI or Anthropic
    if "openai-gpt4o" in orchestrator.get_registered_providers():
        orchestrator.set_lead_provider("openai-gpt4o")
    elif "anthropic-claude" in orchestrator.get_registered_providers():
        orchestrator.set_lead_provider("anthropic-claude")

    # Process a prompt
    prompt = "Explain the benefits of multi-LLM orchestration systems compared to single-model approaches."

    logger.info(f"Processing prompt with SimpleOrchestrator: '{prompt}'")
    result = await orchestrator.process(prompt)

    # Display results summary
    logger.info("=== SimpleOrchestrator Results ===")
    logger.info(f"Number of providers: {len(result['initial_responses'])}")
    logger.info(
        f"Successful responses: {sum(1 for r in result['initial_responses'] if r.get('success', False))}"
    )
    logger.info(f"Analysis type: {result['analysis_results'].get('type')}")

    # Display synthesis
    synthesis = result["synthesis"].get("response", "No synthesis available")
    logger.info(f"Synthesis (truncated): {synthesis[:200]}...")


async def parallel_orchestration_example():
    """Example demonstrating the ParallelOrchestrator."""
    logger.info("\n=== ParallelOrchestrator Example ===")

    # Initialize ParallelOrchestrator
    orchestrator = ParallelOrchestrator(
        max_retries=2,
        timeout_seconds=30,
        use_early_stopping=True,
        min_responses_needed=1,
    )

    # Register providers
    await register_providers(orchestrator)

    # Process a prompt
    prompt = "What are the key considerations when designing a system architecture for a high-throughput API?"

    logger.info(f"Processing prompt with ParallelOrchestrator: '{prompt}'")
    result = await orchestrator.process(prompt)

    # Display results summary
    logger.info("=== ParallelOrchestrator Results ===")
    logger.info(f"Number of providers: {len(result['responses'])}")
    logger.info(
        f"Successful responses: {sum(1 for r in result['responses'] if r.get('success', False))}"
    )
    logger.info(
        f"Early stopping triggered: {result['metadata'].get('early_stopping_triggered', False)}"
    )

    # Display best response
    if result.get("best_response"):
        best_provider = result["best_response"].get("provider_id", "unknown")
        best_response = result["best_response"].get(
            "response", "No best response available"
        )
        logger.info(
            f"Best response from '{best_provider}' (truncated): {best_response[:200]}..."
        )


async def adaptive_orchestration_example():
    """Example demonstrating the AdaptiveOrchestrator."""
    logger.info("\n=== AdaptiveOrchestrator Example ===")

    # Initialize AdaptiveOrchestrator
    orchestrator = AdaptiveOrchestrator(
        max_retries=2,
        timeout_seconds=30,
        default_strategy=OrchestrationStrategy.ADAPTIVE,
        max_providers_per_request=3,
    )

    # Register providers
    await register_providers(orchestrator)

    # Try different strategies
    strategies = [
        (
            OrchestrationStrategy.BALANCED,
            "What are the best practices for API security?",
        ),
        (
            OrchestrationStrategy.QUALITY_OPTIMIZED,
            "Analyze the implications of quantum computing for modern cryptography.",
        ),
        (OrchestrationStrategy.SPEED_OPTIMIZED, "What is the current time in London?"),
    ]

    for strategy, prompt in strategies:
        logger.info(f"\nTrying strategy: {strategy.value}")
        logger.info(f"Processing prompt: '{prompt}'")

        result = await orchestrator.process(prompt, strategy=strategy.value)

        # Display results summary
        logger.info(f"=== Results for {strategy.value} strategy ===")
        logger.info(f"Selected strategy: {result['metadata'].get('strategy')}")

        # For strategies that return responses array
        if "responses" in result:
            logger.info(
                f"Received {sum(1 for r in result['responses'] if r.get('success', False))} successful responses"
            )

            # Show best response if available
            if result.get("best_response"):
                best_provider = result["best_response"].get("provider_id", "unknown")
                best_response = result["best_response"].get(
                    "response", "No best response available"
                )
                logger.info(
                    f"Best response from '{best_provider}' (truncated): {best_response[:200]}..."
                )

        # For strategies that return synthesis
        elif "synthesis" in result:
            logger.info(
                f"Number of providers: {len(result.get('initial_responses', []))}"
            )
            synthesis = result["synthesis"].get("response", "No synthesis available")
            logger.info(f"Synthesis (truncated): {synthesis[:200]}...")


async def main():
    """Run all orchestrator examples."""
    logger.info("Starting orchestrator examples...")

    # Run SimpleOrchestrator example
    await simple_orchestration_example()

    # Run ParallelOrchestrator example
    await parallel_orchestration_example()

    # Run AdaptiveOrchestrator example
    await adaptive_orchestration_example()

    logger.info("Completed all orchestrator examples.")


if __name__ == "__main__":
    asyncio.run(main())

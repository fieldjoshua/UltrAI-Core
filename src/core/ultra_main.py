import asyncio
import os
from typing import Any, Dict, List, Optional

import pandas as pd
from ultra_base import PromptTemplate, RateLimits, UltraBase
from ultra_data import UltraData
from ultra_error_handling import (
    APIError,
    ConfigurationError,
    ErrorTracker,
    RateLimiter,
    RateLimitError,
    UltraError,
    ValidationError,
    handle_api_error,
    handle_configuration_error,
    handle_validation_error,
    validate_api_keys,
    validate_prompt,
)
from ultra_llm import UltraLLM


class UltraOrchestrator:
    def __init__(
        self,
        api_keys: Dict[str, str],
        prompt_templates: Optional[PromptTemplate] = None,
        rate_limits: Optional[RateLimits] = None,
        output_format: str = "plain",
        enabled_features: Optional[List[str]] = None,
        ultra_engine: str = "chatgpt",
    ):
        # Initialize error tracking
        self.error_tracker = ErrorTracker()

        try:
            # Validate API keys
            validate_api_keys(api_keys)

            # Initialize rate limiter
            self.rate_limiter = RateLimiter(requests_per_minute=60)

            # Initialize components
            self.llm = UltraLLM(
                api_keys=api_keys,
                prompt_templates=prompt_templates,
                rate_limits=rate_limits,
                output_format=output_format,
                enabled_features=enabled_features,
                ultra_engine=ultra_engine,
            )

            self.data = UltraData(
                api_keys=api_keys,
                prompt_templates=prompt_templates,
                rate_limits=rate_limits,
                output_format=output_format,
                enabled_features=enabled_features,
            )

            # Store configuration
            self.api_keys = api_keys
            self.prompt_templates = prompt_templates or PromptTemplate()
            self.rate_limits = rate_limits or RateLimits()
            self.output_format = output_format
            self.enabled_features = enabled_features or []
            self.ultra_engine = ultra_engine

        except Exception as e:
            self.error_tracker.add_error(e, {"context": "initialization"})
            raise

    @handle_api_error
    @handle_validation_error
    async def process_with_llm(self, prompt: str) -> Dict[str, str]:
        """Process a prompt through all enabled LLMs."""
        try:
            # Validate prompt
            validate_prompt(prompt)

            # Apply rate limiting
            await self.rate_limiter.acquire()

            responses = {}

            if "openai" in self.enabled_features:
                responses["chatgpt"] = await self.llm.call_chatgpt(prompt)
            if "gemini" in self.enabled_features:
                responses["gemini"] = await self.llm.call_gemini(prompt)
            if "llama" in self.enabled_features:
                responses["llama"] = await self.llm.call_llama(prompt)

            return responses

        except Exception as e:
            self.error_tracker.add_error(
                e,
                {
                    "context": "process_with_llm",
                    "prompt": prompt,
                    "enabled_features": self.enabled_features,
                },
            )
            raise

    @handle_api_error
    @handle_validation_error
    async def process_with_data(
        self,
        data: pd.DataFrame,
        processing_params: Dict[str, Any],
        viz_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process data with optional visualization."""
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()

            results = await self.data.process_data(data, processing_params)

            if viz_params:
                await self.rate_limiter.acquire()
                viz_results = await self.data.visualize_data(data, viz_params)
                results["visualization"] = viz_results

            return results

        except Exception as e:
            self.error_tracker.add_error(
                e,
                {
                    "context": "process_with_data",
                    "processing_params": processing_params,
                    "viz_params": viz_params,
                },
            )
            raise

    @handle_configuration_error
    async def test_all_features(self):
        """Test all enabled features."""
        try:
            # Test LLM features
            if any(
                feature in self.enabled_features
                for feature in ["openai", "gemini", "llama"]
            ):
                test_prompt = "Test prompt for feature testing"
                await self.process_with_llm(test_prompt)

            # Test data processing features
            if "pandas" in self.enabled_features:
                test_data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
                await self.process_with_data(
                    test_data,
                    {"scale": {"method": "standard"}},
                    {"type": "line", "columns": ["A", "B"]},
                )

            return True

        except Exception as e:
            self.error_tracker.add_error(e, {"context": "test_all_features"})
            raise


@handle_configuration_error
async def main():
    try:
        # Load API keys from environment variables
        api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
            "llama": os.getenv("LLAMA_API_KEY"),
        }

        # Initialize orchestrator with all features enabled
        orchestrator = UltraOrchestrator(
            api_keys=api_keys,
            enabled_features=["openai", "gemini", "llama", "pandas", "matplotlib"],
        )

        # Test all features
        await orchestrator.test_all_features()

        # Example usage
        prompt = "Analyze the following data and provide insights: [Your data here]"
        responses = await orchestrator.process_with_llm(prompt)

        # Process data if needed
        data = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [10, 20, 30, 40, 50]})
        results = await orchestrator.process_with_data(
            data,
            {"scale": {"method": "standard"}},
            {"type": "line", "columns": ["A", "B"], "title": "Data Analysis"},
        )

        # Get error summary
        error_summary = orchestrator.error_tracker.get_error_summary()
        print("\nError Summary:", error_summary)

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

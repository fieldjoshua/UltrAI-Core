#!/usr/bin/env python3
"""
LLM Integration Test Script for Ultra MVP

This script validates connections to all supported LLM providers:
- OpenAI (GPT)
- Anthropic (Claude)
- Google (Gemini)
- Local models via Ollama

Usage:
    python llm_integration_test.py
"""

import os
import logging
import asyncio
from typing import Dict
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm-test")

# Load environment variables
load_dotenv()


class LLMTester:
    """Test connectivity to various LLM providers."""

    def __init__(self):
        """Initialize the LLM tester."""
        self.results = {}
        self.test_prompt = (
            "Respond with 'Hello from [MODEL]' where [MODEL] is your model name."
        )

    async def test_openai(self) -> Dict:
        """Test connection to OpenAI API."""
        logger.info("Testing OpenAI connection...")
        result = {"provider": "OpenAI", "status": "failed", "error": None, "models": []}

        try:
            # Import OpenAI library
            from openai import AsyncOpenAI

            # Get API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            # Initialize client
            client = AsyncOpenAI(api_key=api_key)

            # Test API connection by getting models
            models_response = await client.models.list()
            result["models"] = [model.id for model in models_response.data]

            # Test completion
            completion = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": self.test_prompt}],
                max_tokens=20,
            )

            result["response"] = completion.choices[0].message.content
            result["status"] = "success"
            logger.info(f"OpenAI connection successful: {result['response']}")

        except Exception as e:
            error_msg = str(e)
            result["error"] = error_msg
            logger.error(f"OpenAI connection failed: {error_msg}")

        return result

    async def test_anthropic(self) -> Dict:
        """Test connection to Anthropic API."""
        logger.info("Testing Anthropic connection...")
        result = {
            "provider": "Anthropic",
            "status": "failed",
            "error": None,
            "models": [],
        }

        try:
            # Import Anthropic library
            from anthropic import AsyncAnthropic

            # Get API key
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")

            # Initialize client
            client = AsyncAnthropic(api_key=api_key)

            # Test completion
            completion = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=20,
                messages=[{"role": "user", "content": self.test_prompt}],
            )

            result["response"] = completion.content[0].text
            result["models"] = [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ]
            result["status"] = "success"
            logger.info(f"Anthropic connection successful: {result['response']}")

        except Exception as e:
            error_msg = str(e)
            result["error"] = error_msg
            logger.error(f"Anthropic connection failed: {error_msg}")

        return result

    async def test_gemini(self) -> Dict:
        """Test connection to Google Gemini API."""
        logger.info("Testing Google Gemini connection...")
        result = {
            "provider": "Google Gemini",
            "status": "failed",
            "error": None,
            "models": [],
        }

        try:
            # Import Google Generative AI library
            import google.generativeai as genai

            # Get API key
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")

            # Initialize client
            genai.configure(api_key=api_key)

            # List available models
            models = genai.list_models()
            result["models"] = [model.name for model in models]

            # Test text generation
            model = genai.GenerativeModel("gemini-pro")
            response = await model.generate_content_async(self.test_prompt)

            result["response"] = response.text
            result["status"] = "success"
            logger.info(f"Google Gemini connection successful: {result['response']}")

        except Exception as e:
            error_msg = str(e)
            result["error"] = error_msg
            logger.error(f"Google Gemini connection failed: {error_msg}")

        return result

    async def test_ollama(self) -> Dict:
        """Test connection to Ollama local API."""
        logger.info("Testing Ollama connection...")
        result = {"provider": "Ollama", "status": "failed", "error": None, "models": []}

        try:
            # Import requests for API calls
            import httpx

            # Get Ollama base URL
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

            # Test connection to API
            async with httpx.AsyncClient() as client:
                # Check if Ollama is running by listing models
                response = await client.get(f"{base_url}/api/tags")
                if response.status_code != 200:
                    raise Exception(
                        f"Failed to connect to Ollama API: {response.status_code}"
                    )

                models_data = response.json()
                result["models"] = [
                    model["name"] for model in models_data.get("models", [])
                ]

                # Test generating with a simple model (if available)
                if result["models"]:
                    test_model = result["models"][0]
                    generate_response = await client.post(
                        f"{base_url}/api/generate",
                        json={
                            "model": test_model,
                            "prompt": self.test_prompt,
                            "stream": False,
                        },
                    )

                    if generate_response.status_code == 200:
                        result["response"] = generate_response.json().get(
                            "response", "No response"
                        )
                        result["status"] = "success"
                        logger.info(
                            f"Ollama connection successful: {result['response']}"
                        )
                    else:
                        raise Exception(
                            f"Failed to generate response: {generate_response.status_code}"
                        )
                else:
                    result["error"] = "No models available in Ollama"

        except Exception as e:
            error_msg = str(e)
            result["error"] = error_msg
            logger.error(f"Ollama connection failed: {error_msg}")

        return result

    async def run_all_tests(self) -> Dict:
        """Run all LLM connection tests."""
        logger.info("Starting LLM integration tests...")

        # Run all tests
        tasks = [
            self.test_openai(),
            self.test_anthropic(),
            self.test_gemini(),
            self.test_ollama(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        test_results = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                provider = ["OpenAI", "Anthropic", "Google Gemini", "Ollama"][i]
                test_results[provider] = {
                    "provider": provider,
                    "status": "failed",
                    "error": str(result),
                    "models": [],
                }
            else:
                test_results[result["provider"]] = result

        self.results = test_results
        return test_results

    def print_results(self):
        """Print the test results in a formatted manner."""
        print("\n" + "=" * 60)
        print("ULTRA MVP LLM INTEGRATION TEST RESULTS")
        print("=" * 60)

        for provider, result in self.results.items():
            status = "✅ SUCCESS" if result["status"] == "success" else "❌ FAILED"
            print(f"\n{provider} Integration: {status}")

            if result["status"] == "success":
                print(f"  Response: {result['response']}")
                # Format model list with first 3 models and ellipsis if needed
                models_str = ", ".join(result["models"][:3])
                if len(result["models"]) > 3:
                    models_str += "..."
                print(f"  Available models: {models_str}")
            else:
                print(f"  Error: {result['error']}")

        print("\n" + "=" * 60)

        # Print summary
        success_count = sum(
            1 for r in self.results.values() if r["status"] == "success"
        )
        total_count = len(self.results)
        print(f"\nSummary: {success_count}/{total_count} integrations successful")
        print("=" * 60 + "\n")


async def main():
    """Run the LLM integration tests."""
    tester = LLMTester()
    await tester.run_all_tests()
    tester.print_results()


if __name__ == "__main__":
    asyncio.run(main())

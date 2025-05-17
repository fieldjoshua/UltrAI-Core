"""
Ultra LLM Core Module

This module implements the UltraLLM class, which provides a unified interface
for interacting with multiple LLM providers.
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union

try:
    # Optional imports for different LLM providers
    import anthropic
    import google.generativeai as genai
    import httpx
    import openai
except ImportError as e:
    logging.warning(f"Some LLM provider libraries not installed: {e}")

from src.models.model_response import ModelResponse
from src.utils.cache import SimpleCache, cached

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ultra-llm")


class UltraLLM:
    """
    Unified interface for multiple LLM providers.

    This class handles the initialization and communication with various
    LLM providers, providing a standardized way to interact with them.
    """

    def __init__(
        self,
        api_keys: Optional[Dict[str, str]] = None,
        enabled_features: Optional[List[str]] = None,
        cache_ttl: int = 3600,
    ):
        """
        Initialize the UltraLLM instance.

        Args:
            api_keys: Dictionary with API keys for different providers
            enabled_features: List of enabled LLM features/providers
            cache_ttl: Cache time-to-live in seconds
        """
        self.api_keys = api_keys or {}
        self.enabled_features = enabled_features or [
            "openai",
            "anthropic",
            "gemini",
            "mistral",
        ]
        self.available_models = []
        self.clients = {}
        self.cache = SimpleCache(ttl=cache_ttl)

        # Load API keys from environment if not provided
        if not self.api_keys:
            self._load_api_keys_from_env()

    def _load_api_keys_from_env(self) -> None:
        """Load API keys from environment variables."""
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
            "mistral": os.getenv("MISTRAL_API_KEY"),
            "llama": os.getenv("LLAMA_API_KEY"),
        }

    def _initialize_clients(self) -> None:
        """Initialize clients for all enabled LLM providers."""
        # Initialize OpenAI client
        if "openai" in self.enabled_features and self.api_keys.get("openai"):
            try:
                self.clients["openai"] = openai.OpenAI(api_key=self.api_keys["openai"])
                self.available_models.append("openai")
                logger.info("OpenAI client initialized")
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

        # Initialize Anthropic client
        if "anthropic" in self.enabled_features and self.api_keys.get("anthropic"):
            try:
                self.clients["anthropic"] = anthropic.Anthropic(
                    api_key=self.api_keys["anthropic"]
                )
                self.available_models.append("anthropic")
                logger.info("Anthropic client initialized")
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")

        # Initialize Google client
        if "gemini" in self.enabled_features and self.api_keys.get("google"):
            try:
                genai.configure(api_key=self.api_keys["google"])
                self.clients["gemini"] = genai
                self.available_models.append("gemini")
                logger.info("Google Gemini client initialized")
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize Google client: {e}")

        # Initialize Mistral client
        if "mistral" in self.enabled_features and self.api_keys.get("mistral"):
            try:
                # Using httpx for Mistral API (simplified for MVP)
                self.clients["mistral"] = httpx.AsyncClient(
                    base_url="https://api.mistral.ai/v1",
                    headers={"Authorization": f"Bearer {self.api_keys['mistral']}"},
                )
                self.available_models.append("mistral")
                logger.info("Mistral client initialized")
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize Mistral client: {e}")

        # Initialize Ollama client if enabled
        if "ollama" in self.enabled_features:
            try:
                ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                self.clients["ollama"] = httpx.AsyncClient(base_url=ollama_url)
                self.available_models.append("ollama")
                logger.info("Ollama client initialized")
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize Ollama client: {e}")

        # Initialize LLaMA API client if enabled
        if "llama" in self.enabled_features and self.api_keys.get("llama"):
            try:
                # Using httpx for LLaMA API (simplified for MVP)
                self.clients["llama"] = httpx.AsyncClient(
                    headers={"Authorization": f"Bearer {self.api_keys['llama']}"}
                )
                self.available_models.append("llama")
                logger.info("LLaMA client initialized")
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize LLaMA client: {e}")

    async def analyze_prompt(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        ultra_model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Analyze a prompt using multiple LLMs.

        Args:
            prompt: The prompt to analyze
            models: List of models to use (default: all available)
            ultra_model: Model to use for synthesis (optional)
            temperature: Temperature parameter for LLM generation
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with responses from all models and optional synthesis
        """
        # Initialize clients if not already done
        if not self.clients:
            self._initialize_clients()

        # Use all available models if none specified
        models = models or self.available_models

        # Filter to only available models
        models = [model for model in models if model in self.available_models]

        if not models:
            return {
                "status": "error",
                "message": "No valid models available",
                "results": {},
            }

        # Start timer
        start_time = time.time()

        # Prepare tasks for each model
        tasks = []
        for model in models:
            if model == "openai":
                tasks.append(self.get_chatgpt_response(prompt, temperature, max_tokens))
            elif model == "anthropic":
                tasks.append(self.get_claude_response(prompt, temperature, max_tokens))
            elif model == "gemini":
                tasks.append(self.get_gemini_response(prompt, temperature, max_tokens))
            elif model == "mistral":
                tasks.append(self.get_mistral_response(prompt, temperature, max_tokens))
            elif model == "ollama":
                tasks.append(self.call_ollama(prompt, temperature, max_tokens))
            elif model == "llama":
                tasks.append(self.call_llama(prompt, temperature, max_tokens))

        # Run all tasks concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process responses
        model_responses = {}
        for i, model in enumerate(models):
            response = responses[i]
            if isinstance(response, Exception):
                model_responses[model] = ModelResponse(
                    model_name=model,
                    error=str(response),
                ).to_dict()
            else:
                model_responses[model] = response.to_dict()

        # Create Ultra synthesis if requested
        ultra_response = None
        if ultra_model and ultra_model in self.available_models:
            synthesis_prompt = f"""
            I have received the following responses from different language models to this prompt:

            PROMPT: {prompt}

            RESPONSES:
            {chr(10).join([f"{model}: {resp.get('content', 'Error: ' + resp.get('error', 'No response'))}"
                           for model, resp in model_responses.items()])}

            Please synthesize these responses into a comprehensive answer that captures
            the best insights from each model while addressing any contradictions.
            """

            if ultra_model == "openai":
                synthesis = await self.get_chatgpt_response(
                    synthesis_prompt, 0.3, max_tokens
                )
            elif ultra_model == "anthropic":
                synthesis = await self.get_claude_response(
                    synthesis_prompt, 0.3, max_tokens
                )
            elif ultra_model == "gemini":
                synthesis = await self.get_gemini_response(
                    synthesis_prompt, 0.3, max_tokens
                )
            else:
                # Default to first available model if ultra_model is not directly supported
                if "openai" in self.available_models:
                    synthesis = await self.get_chatgpt_response(
                        synthesis_prompt, 0.3, max_tokens
                    )
                elif "anthropic" in self.available_models:
                    synthesis = await self.get_claude_response(
                        synthesis_prompt, 0.3, max_tokens
                    )
                else:
                    synthesis = ModelResponse(
                        model_name="ultra",
                        error="No suitable model available for synthesis",
                    )

            ultra_response = synthesis.to_dict()

        # Calculate total processing time
        total_time = time.time() - start_time

        return {
            "status": "success",
            "results": {
                "model_responses": model_responses,
                "ultra_response": ultra_response,
                "total_time": total_time,
            },
        }

    @cached(ttl=3600)
    async def get_chatgpt_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        """
        Get response from OpenAI's ChatGPT.

        Args:
            prompt: The prompt to send
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            ModelResponse object with the response
        """
        if "openai" not in self.clients:
            return ModelResponse(
                model_name="openai",
                error="OpenAI client not initialized",
            )

        start_time = time.time()

        try:
            client = self.clients["openai"]
            response = client.chat.completions.create(
                model="gpt-4o",  # Use latest model
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            tokens = response.usage.total_tokens

            model_response = ModelResponse(
                model_name="openai",
                content=content,
                tokens_used=tokens,
            )

            # Set processing time
            model_response.set_processing_time(time.time() - start_time)

            return model_response

        except Exception as e:
            logger.error(f"Error getting ChatGPT response: {e}")
            return ModelResponse(
                model_name="openai",
                error=str(e),
            )

    @cached(ttl=3600)
    async def get_claude_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        """
        Get response from Anthropic's Claude.

        Args:
            prompt: The prompt to send
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            ModelResponse object with the response
        """
        if "anthropic" not in self.clients:
            return ModelResponse(
                model_name="anthropic",
                error="Anthropic client not initialized",
            )

        start_time = time.time()

        try:
            client = self.clients["anthropic"]
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text

            model_response = ModelResponse(
                model_name="anthropic",
                content=content,
                tokens_used=None,  # Anthropic doesn't return token count directly
            )

            # Set processing time
            model_response.set_processing_time(time.time() - start_time)

            return model_response

        except Exception as e:
            logger.error(f"Error getting Claude response: {e}")
            return ModelResponse(
                model_name="anthropic",
                error=str(e),
            )

    @cached(ttl=3600)
    async def get_gemini_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        """
        Get response from Google's Gemini.

        Args:
            prompt: The prompt to send
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            ModelResponse object with the response
        """
        if "gemini" not in self.clients:
            return ModelResponse(
                model_name="gemini",
                error="Google Gemini client not initialized",
            )

        start_time = time.time()

        try:
            genai = self.clients["gemini"]
            model = genai.GenerativeModel("gemini-1.5-pro")

            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            content = response.text

            model_response = ModelResponse(
                model_name="gemini",
                content=content,
            )

            # Set processing time
            model_response.set_processing_time(time.time() - start_time)

            return model_response

        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            return ModelResponse(
                model_name="gemini",
                error=str(e),
            )

    @cached(ttl=3600)
    async def get_mistral_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        """
        Get response from Mistral AI.

        Args:
            prompt: The prompt to send
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            ModelResponse object with the response
        """
        if "mistral" not in self.clients:
            return ModelResponse(
                model_name="mistral",
                error="Mistral client not initialized",
            )

        start_time = time.time()

        try:
            client = self.clients["mistral"]

            response = await client.post(
                "/chat/completions",
                json={
                    "model": "mistral-large-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            if response.status_code != 200:
                return ModelResponse(
                    model_name="mistral",
                    error=f"API error: {response.status_code} - {response.text}",
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            model_response = ModelResponse(
                model_name="mistral",
                content=content,
            )

            # Set processing time
            model_response.set_processing_time(time.time() - start_time)

            return model_response

        except Exception as e:
            logger.error(f"Error getting Mistral response: {e}")
            return ModelResponse(
                model_name="mistral",
                error=str(e),
            )

    @cached(ttl=3600)
    async def call_ollama(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        """
        Get response from local Ollama model.

        Args:
            prompt: The prompt to send
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            ModelResponse object with the response
        """
        if "ollama" not in self.clients:
            return ModelResponse(
                model_name="ollama",
                error="Ollama client not initialized",
            )

        start_time = time.time()

        try:
            client = self.clients["ollama"]
            model_name = os.getenv("OLLAMA_MODEL", "llama3")

            response = await client.post(
                "/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )

            if response.status_code != 200:
                return ModelResponse(
                    model_name="ollama",
                    error=f"API error: {response.status_code} - {response.text}",
                )

            data = response.json()
            content = data.get("response", "")

            model_response = ModelResponse(
                model_name="ollama",
                content=content,
            )

            # Set processing time
            model_response.set_processing_time(time.time() - start_time)

            return model_response

        except Exception as e:
            logger.error(f"Error getting Ollama response: {e}")
            return ModelResponse(
                model_name="ollama",
                error=str(e),
            )

    @cached(ttl=3600)
    async def call_llama(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        """
        Get response from LLaMA API.

        Args:
            prompt: The prompt to send
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            ModelResponse object with the response
        """
        if "llama" not in self.clients:
            return ModelResponse(
                model_name="llama",
                error="LLaMA client not initialized",
            )

        start_time = time.time()

        try:
            client = self.clients["llama"]
            llama_url = os.getenv("LLAMA_API_URL", "https://api.llama-api.com")

            response = await client.post(
                f"{llama_url}/v1/chat/completions",
                json={
                    "model": "llama-3-70b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            if response.status_code != 200:
                return ModelResponse(
                    model_name="llama",
                    error=f"API error: {response.status_code} - {response.text}",
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            model_response = ModelResponse(
                model_name="llama",
                content=content,
            )

            # Set processing time
            model_response.set_processing_time(time.time() - start_time)

            return model_response

        except Exception as e:
            logger.error(f"Error getting LLaMA response: {e}")
            return ModelResponse(
                model_name="llama",
                error=str(e),
            )

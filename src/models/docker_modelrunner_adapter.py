"""
Docker Model Runner Adapter Module.

This module provides an adapter for the Docker Model Runner, allowing Ultra to use
locally-run open-source LLMs through Docker's Model Runner plugin.
"""

import asyncio
import logging
import os
import time
from typing import Any, AsyncGenerator, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from src.models.llm_adapter import LLMAdapter

# Import URL validation utilities if available
try:
    from backend.utils.validation import validate_url, is_url_safe
    URL_VALIDATION_AVAILABLE = True
except ImportError:
    # Create stub functions if validation module is not available
    def validate_url(url, check_ips=True):
        """Stub function when validation module is not available."""
        return True
        
    def is_url_safe(url, check_ips=True):
        """Stub function when validation module is not available."""
        return True
        
    URL_VALIDATION_AVAILABLE = False


class DockerModelRunnerAdapter(LLMAdapter):
    """Adapter for Docker Model Runner LLMs."""

    def __init__(self, api_key: Optional[str] = None, model: str = "phi3:mini", **kwargs):
        """
        Initialize the Docker Model Runner adapter.

        Args:
            api_key: Optional API key (not required for Model Runner)
            model: The model to use (default: "phi3:mini")
            **kwargs: Additional options including:
                base_url: API endpoint URL (default: http://model-runner:8080)
        """
        super().__init__(name="docker_modelrunner", api_key=api_key)
        
        # Extract and validate base_url if provided
        base_url = kwargs.get("base_url", os.environ.get("MODEL_RUNNER_URL", "http://model-runner:8080"))
        if base_url and URL_VALIDATION_AVAILABLE:
            try:
                validate_url(base_url)
                self.logger.info(f"Using Docker Model Runner URL: {base_url}")
                self.base_url = base_url
            except ValueError as e:
                self.logger.warning(f"Invalid base URL, using default: {e}")
                self.base_url = "http://model-runner:8080"
        else:
            self.base_url = base_url
            
        self.model = model
        self.rate_limit_seconds = 0.2  # Rate limiting
        self.logger = logging.getLogger(f"docker_modelrunner_adapter.{model}")
        self.timeout = kwargs.get("timeout", int(os.environ.get("LOCAL_MODEL_TIMEOUT", 60000)) / 1000)

    @retry(
        stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=3)
    )
    async def generate(self, prompt: str, **options) -> str:
        """
        Generate a response from Docker Model Runner.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 1000)
                temperature: Temperature (default: 0.7)
                system_message: System message (default: "You are a helpful assistant.")

        Returns:
            The generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 1000)
            temperature = options.get("temperature", 0.7)
            system_msg = options.get("system_message", "You are a helpful assistant.")

            self.logger.debug(
                f"Calling Docker Model Runner model {model} with prompt: {prompt[:50]}..."
            )
            
            async with aiohttp.ClientSession() as session:
                # Prepare the request in OpenAI format since Model Runner uses OpenAI-compatible API
                request_data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=request_data,
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Docker Model Runner error: {response.status} - {error_text}")
                        raise Exception(f"Model Runner API returned status {response.status}: {error_text}")
                    
                    result = await response.json()
                    
            self.logger.debug(f"Docker Model Runner call successful for model {model}")
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            self.logger.error(
                f"Docker Model Runner API call failed for model {options.get('model', self.model)}: {e}",
                exc_info=True,
            )
            raise

    async def stream_generate(
        self, prompt: str, **options
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from Docker Model Runner.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 1000)
                temperature: Temperature (default: 0.7)
                system_message: System message (default: "You are a helpful assistant.")

        Yields:
            Chunks of the generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 1000)
            temperature = options.get("temperature", 0.7)
            system_msg = options.get("system_message", "You are a helpful assistant.")

            self.logger.debug(
                f"Streaming from Docker Model Runner model {model} with prompt: {prompt[:50]}..."
            )
            
            async with aiohttp.ClientSession() as session:
                # Prepare the request in OpenAI format
                request_data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": True
                }
                
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=request_data,
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Docker Model Runner streaming error: {response.status} - {error_text}")
                        raise Exception(f"Model Runner API returned status {response.status}: {error_text}")
                    
                    # Process the streaming response
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if not line or line == "data: [DONE]":
                            continue
                        
                        if line.startswith("data: "):
                            try:
                                import json
                                data = json.loads(line[6:])  # Remove "data: " prefix
                                
                                if "choices" in data and data["choices"] and "delta" in data["choices"][0]:
                                    content = data["choices"][0]["delta"].get("content", "")
                                    if content:
                                        yield content
                            except Exception as e:
                                self.logger.error(f"Error parsing streaming response: {e}")
                                # Continue processing other chunks even if one fails
            
            self.logger.debug(f"Docker Model Runner streaming call completed for model {model}")

        except Exception as e:
            self.logger.error(f"Docker Model Runner streaming API call failed: {e}")
            raise

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from Docker Model Runner.
        
        Returns:
            List of available models with their details
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v1/models",
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Failed to get available models: {response.status} - {error_text}")
                        return []
                    
                    result = await response.json()
                    
                    if "data" in result:
                        return result["data"]
                    return []
                    
        except Exception as e:
            self.logger.error(f"Failed to get available models: {e}")
            return []

    async def check_availability(self) -> bool:
        """
        Check if Docker Model Runner is available.

        Returns:
            True if Docker Model Runner is available, False otherwise
        """
        try:
            # Check if we can connect to the API and get models
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v1/models", 
                    timeout=5  # Short timeout for availability check
                ) as response:
                    return response.status == 200
        except Exception as e:
            self.logger.warning(f"Docker Model Runner availability check failed: {e}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Docker Model Runner capabilities."""
        capabilities = super().get_capabilities()
        
        # Model-specific capabilities
        if "llama3" in self.model:
            max_tokens = 8192 if "70b" in self.model else 4096
        elif "phi3" in self.model:
            max_tokens = 2048 if "mini" in self.model else 4096
        elif "mistral" in self.model:
            max_tokens = 8192 if "large" in self.model else 4096
        else:
            max_tokens = 4096  # Default
        
        capabilities.update({
            "name": f"local-{self.model}",
            "supports_streaming": True,
            "max_tokens": max_tokens,
            "supports_vision": False,  # Most local models don't support vision yet
            "source": "local",
        })
        return capabilities


# Helper function to create Docker Model Runner adapter
def create_modelrunner_adapter(model: str = "phi3:mini", **kwargs) -> DockerModelRunnerAdapter:
    """
    Create a Docker Model Runner adapter for the specified model.
    
    Args:
        model: The model to use (default: "phi3:mini")
        **kwargs: Additional options
        
    Returns:
        DockerModelRunnerAdapter instance
    """
    base_url = kwargs.get("base_url", os.environ.get("MODEL_RUNNER_URL", "http://model-runner:8080"))
    timeout = kwargs.get("timeout", int(os.environ.get("LOCAL_MODEL_TIMEOUT", 60000)))
    
    return DockerModelRunnerAdapter(model=model, base_url=base_url, timeout=timeout)


# Function to get all available Docker Model Runner models
async def get_available_models(base_url: Optional[str] = None) -> List[str]:
    """
    Get all available models from Docker Model Runner.
    
    Args:
        base_url: Model Runner API URL (optional)
        
    Returns:
        List of model IDs
    """
    try:
        adapter = create_modelrunner_adapter(base_url=base_url)
        models = await adapter.get_available_models()
        return [model["id"] for model in models]
    except Exception as e:
        logging.error(f"Failed to get available models: {e}")
        return []
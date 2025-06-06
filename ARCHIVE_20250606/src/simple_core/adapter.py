"""
Adapter module for Simple Core Orchestrator.

This module provides the adapter interface and implementations for different
LLM providers with a focus on simplicity and directness.
"""

import asyncio
import json
import logging
import os
import subprocess
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional

import google.generativeai as genai
from anthropic import AsyncAnthropic

# Import provider-specific libraries
from openai import AsyncOpenAI

from src.simple_core.config import ModelDefinition


class Adapter(ABC):
    """Minimal adapter interface for LLM providers."""

    def __init__(self, model_def: ModelDefinition):
        """
        Initialize the adapter with a model definition.

        Args:
            model_def: Definition for the model to use
        """
        self.model_def = model_def
        self.name = model_def.name
        self.provider = model_def.provider
        self.api_key = model_def.api_key
        self.options = model_def.options
        self.logger = logging.getLogger(f"simple_core.adapter.{self.provider}")

    @abstractmethod
    async def generate(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The input prompt
            options: Additional provider-specific options

        Returns:
            The generated text response
        """
        pass

    async def check_availability(self) -> bool:
        """
        Check if the LLM is available.

        Returns:
            True if available, False otherwise
        """
        try:
            # Simple availability check - attempt to generate a short response
            response = await self.generate("Test availability", {"max_tokens": 5})
            return bool(response)
        except Exception as e:
            self.logger.warning(f"Availability check failed: {e}")
            return False


class OpenAIAdapter(Adapter):
    """Adapter for OpenAI models."""

    def __init__(self, model_def: ModelDefinition):
        """Initialize the OpenAI adapter."""
        super().__init__(model_def)

        # Get API key from model_def or environment
        api_key = model_def.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")

        # Initialize the client
        self.client = AsyncOpenAI(api_key=api_key)

        # Get model ID from options or use default
        self.model_id = model_def.options.get("model_id", "gpt-4o")
        self.logger.info(f"Initialized OpenAIAdapter for model {self.model_id}")

    async def generate(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a response from OpenAI.

        Args:
            prompt: The prompt to send
            options: Additional options

        Returns:
            The generated text
        """
        options = options or {}

        # Extract options with defaults
        max_tokens = options.get("max_tokens", 1000)
        temperature = options.get("temperature", 0.7)
        system_message = options.get("system_message", "You are a helpful assistant.")

        try:
            # Call the OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract and return the response text
            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise


class AnthropicAdapter(Adapter):
    """Adapter for Anthropic Claude models."""

    def __init__(self, model_def: ModelDefinition):
        """Initialize the Anthropic adapter."""
        super().__init__(model_def)

        # Get API key from model_def or environment
        api_key = model_def.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key is required")

        # Initialize the client
        self.client = AsyncAnthropic(api_key=api_key)

        # Get model ID from options or use default
        self.model_id = model_def.options.get("model_id", "claude-3-opus-20240229")
        self.logger.info(f"Initialized AnthropicAdapter for model {self.model_id}")

    async def generate(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a response from Anthropic Claude.

        Args:
            prompt: The prompt to send
            options: Additional options

        Returns:
            The generated text
        """
        options = options or {}

        # Extract options with defaults
        max_tokens = options.get("max_tokens", 1000)
        temperature = options.get("temperature", 0.7)
        system_message = options.get("system_message")

        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]

            # Add system message if provided
            kwargs = {}
            if system_message:
                kwargs["system"] = system_message

            # Call the Anthropic API
            response = await self.client.messages.create(
                model=self.model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            # Extract and return the response text
            return response.content[0].text

        except Exception as e:
            self.logger.error(f"Anthropic API error: {str(e)}")
            raise


class GeminiAdapter(Adapter):
    """Adapter for Google Gemini models."""

    def __init__(self, model_def: ModelDefinition):
        """Initialize the Gemini adapter."""
        super().__init__(model_def)

        # Get API key from model_def or environment
        api_key = model_def.api_key or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key is required")

        # Initialize the client
        genai.configure(api_key=api_key)

        # Get model ID from options or use default
        self.model_id = model_def.options.get("model_id", "gemini-1.5-pro-latest")
        self.logger.info(f"Initialized GeminiAdapter for model {self.model_id}")

        # Create the model
        self.model = genai.GenerativeModel(self.model_id)

    async def generate(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a response from Google Gemini.

        Args:
            prompt: The prompt to send
            options: Additional options

        Returns:
            The generated text
        """
        options = options or {}

        # Extract options with defaults
        temperature = options.get("temperature", 0.7)

        try:
            # Call the Gemini API (uses async method if available)
            generation_config = {"temperature": temperature}

            # Use appropriate async method for Gemini
            try:
                # Try the async method first
                response = await self.model.generate_content_async(
                    prompt, generation_config=generation_config
                )
            except AttributeError:
                # Fallback to sync method in asyncio executor if async not available
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(
                        prompt, generation_config=generation_config
                    ),
                )

            # Extract and return the response text
            return response.text

        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            raise


class LlamaAdapter(Adapter):
    """Adapter for local Llama models using llama.cpp or similar."""

    def __init__(self, model_def: ModelDefinition):
        """Initialize the Llama adapter."""
        super().__init__(model_def)

        # Get model path from options
        self.model_path = model_def.options.get("model_path")
        if not self.model_path:
            raise ValueError("model_path is required for Llama models")

        # Check if the model file exists
        if not os.path.exists(self.model_path):
            raise ValueError(f"Model file not found: {self.model_path}")

        # Get command or binary to use for generation
        self.command = model_def.options.get("command", "llama")

        # Get additional arguments
        self.extra_args = model_def.options.get("extra_args", [])

        self.logger.info(f"Initialized LlamaAdapter for model at {self.model_path}")

    async def generate(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a response from local Llama model.

        Args:
            prompt: The prompt to send
            options: Additional options

        Returns:
            The generated text
        """
        options = options or {}

        # Extract options with defaults
        max_tokens = options.get("max_tokens", 1000)
        temperature = options.get("temperature", 0.7)

        try:
            # Prepare the command
            cmd = [
                self.command,
                "-m",
                self.model_path,
                "--temp",
                str(temperature),
                "-n",
                str(max_tokens),
                "-p",
                prompt,
            ]

            # Add extra arguments
            cmd.extend(self.extra_args)

            # Execute the command in a subprocess
            self.logger.info(f"Running command: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            # Wait for the process to complete
            stdout, stderr = await process.communicate()

            # Check if the process was successful
            if process.returncode != 0:
                self.logger.error(f"Llama process error: {stderr.decode('utf-8')}")
                raise RuntimeError(
                    f"Llama process failed with code {process.returncode}"
                )

            # Return the output
            output = stdout.decode("utf-8")

            # Most llama.cpp implementations prepend the prompt to the output
            # So remove the prompt from the beginning of the output
            if output.startswith(prompt):
                output = output[len(prompt) :].strip()

            return output

        except Exception as e:
            self.logger.error(f"Llama generation error: {str(e)}")
            raise

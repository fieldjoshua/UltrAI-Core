"""
Unified and simplified LLM adapters with proper async support and timeouts.

This file consolidates the adapters for OpenAI, Anthropic, and Google
into a single location, using the modern `httpx` library for true asynchronous
requests and robust network timeouts.
"""

import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# A single, shared async client for all adapters to use
# This is best practice for performance and resource management.
# Timeout is set to 25 seconds for all network operations.
CLIENT = httpx.AsyncClient(timeout=25.0)


class BaseAdapter:
    """A simplified base adapter for all LLM providers."""

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError(f"API key for {self.__class__.__name__} is missing.")
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Placeholder for the generate method."""
        raise NotImplementedError


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI models using httpx."""

    async def generate(self, prompt: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            response = await CLIENT.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return {"generated_text": data["choices"][0]["message"]["content"]}
        except httpx.ReadTimeout:
            logger.warning(f"OpenAI request timed out for model {self.model}.")
            return {"generated_text": "Error: OpenAI request timed out."}
        except Exception as e:
            logger.error(f"OpenAI API error for model {self.model}: {e}")
            return {
                "generated_text": f"Error: An issue occurred with the OpenAI API: {e}"
            }


class AnthropicAdapter(BaseAdapter):
    """Adapter for Anthropic models using httpx."""

    async def generate(self, prompt: str) -> Dict[str, Any]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            response = await CLIENT.post(
                "https://api.anthropic.com/v1/messages", headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()
            return {"generated_text": data["content"][0]["text"]}
        except httpx.ReadTimeout:
            logger.warning(f"Anthropic request timed out for model {self.model}.")
            return {"generated_text": "Error: Anthropic request timed out."}
        except Exception as e:
            logger.error(f"Anthropic API error for model {self.model}: {e}")
            return {
                "generated_text": f"Error: An issue occurred with the Anthropic API: {e}"
            }


class GeminiAdapter(BaseAdapter):
    """Adapter for Google Gemini models using httpx."""

    async def generate(self, prompt: str) -> Dict[str, Any]:
        # Note: The URL is specific to the model and includes the API key.
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = await CLIENT.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return {
                "generated_text": data["candidates"][0]["content"]["parts"][0]["text"]
            }
        except httpx.ReadTimeout:
            logger.warning(f"Google Gemini request timed out for model {self.model}.")
            return {"generated_text": "Error: Google Gemini request timed out."}
        except Exception as e:
            logger.error(f"Google Gemini API error for model {self.model}: {e}")
            return {
                "generated_text": f"Error: An issue occurred with the Google Gemini API: {e}"
            }

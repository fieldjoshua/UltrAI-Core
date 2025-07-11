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
# Timeout is set to 45 seconds for all network operations (Ultra Synthesis pipeline needs more time).
CLIENT = httpx.AsyncClient(timeout=45.0)


class BaseAdapter:
    """A simplified base adapter for all LLM providers."""

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError(f"API key for {self.__class__.__name__} is missing.")
        self.api_key = api_key
        self.model = model

    def _mask_api_key(self, api_key: str) -> str:
        """Mask API key for secure logging."""
        if len(api_key) <= 8:
            return "***"
        return f"{api_key[:4]}***{api_key[-4:]}"

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
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                masked_key = self._mask_api_key(self.api_key)
                logger.error(
                    f"OpenAI API authentication failed for model {self.model}: Invalid API key ({masked_key})"
                )
                return {
                    "generated_text": "Error: OpenAI API authentication failed. Check API key."
                }
            elif e.response.status_code == 404:
                logger.error(f"OpenAI API 404 for model {self.model}: Model not found")
                return {
                    "generated_text": f"Error: Model {self.model} not found in OpenAI API"
                }
            elif e.response.status_code == 429:
                logger.warning(
                    f"OpenAI API rate-limited for model {self.model}. Returning standard retry message."
                )
                return {
                    "generated_text": "Error: OpenAI API rate limit exceeded. Please retry later."
                }
            else:
                logger.error(
                    f"OpenAI API HTTP error for model {self.model}: {e.response.status_code} - {e}"
                )
                return {
                    "generated_text": f"Error: OpenAI API HTTP {e.response.status_code}: {e}"
                }
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
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error(
                    f"Anthropic API authentication failed for model {self.model}: Invalid API key"
                )
                return {
                    "generated_text": "Error: Anthropic API authentication failed. Check API key."
                }
            elif e.response.status_code == 404:
                logger.error(
                    f"Anthropic API 404 for model {self.model}: Model not found or invalid endpoint"
                )
                return {
                    "generated_text": f"Error: Model {self.model} not found in Anthropic API"
                }
            else:
                logger.error(
                    f"Anthropic API HTTP error for model {self.model}: {e.response.status_code} - {e}"
                )
                return {
                    "generated_text": f"Error: Anthropic API HTTP {e.response.status_code}: {e}"
                }
        except Exception as e:
            logger.error(f"Anthropic API error for model {self.model}: {e}")
            return {
                "generated_text": f"Error: An issue occurred with the Anthropic API: {e}"
            }


class GeminiAdapter(BaseAdapter):
    """Adapter for Google Gemini models using httpx."""

    async def generate(self, prompt: str) -> Dict[str, Any]:
        # SECURITY FIX: Move API key from URL to secure header
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
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
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                logger.error(
                    f"Google Gemini API 400 for model {self.model}: Bad request or invalid model"
                )
                return {
                    "generated_text": f"Error: Invalid request or model {self.model} not available in Gemini API"
                }
            elif e.response.status_code == 401:
                logger.error(
                    f"Google Gemini API authentication failed for model {self.model}: Invalid API key"
                )
                return {
                    "generated_text": "Error: Google Gemini API authentication failed. Check API key."
                }
            elif e.response.status_code == 404:
                logger.error(
                    f"Google Gemini API 404 for model {self.model}: Model not found"
                )
                return {
                    "generated_text": f"Error: Model {self.model} not found in Google Gemini API"
                }
            else:
                logger.error(
                    f"Google Gemini API HTTP error for model {self.model}: {e.response.status_code} - {e}"
                )
                return {
                    "generated_text": f"Error: Google Gemini API HTTP {e.response.status_code}: {e}"
                }
        except Exception as e:
            logger.error(f"Google Gemini API error for model {self.model}: {e}")
            return {
                "generated_text": f"Error: An issue occurred with the Google Gemini API: {e}"
            }


class HuggingFaceAdapter(BaseAdapter):
    """Adapter for Hugging Face Inference API models using httpx."""

    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        # Hugging Face model ID format: "meta-llama/Llama-2-7b-chat-hf"
        self.model_id = model

    async def generate(self, prompt: str) -> Dict[str, Any]:
        url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Different payload format for different model types
        if "llama" in self.model_id.lower() or "mistral" in self.model_id.lower():
            # Chat models
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False,
                },
            }
        else:
            # Text generation models
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False,
                },
            }

        try:
            response = await CLIENT.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Handle different response formats
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict) and "generated_text" in data[0]:
                    return {"generated_text": data[0]["generated_text"]}
                elif isinstance(data[0], str):
                    return {"generated_text": data[0]}
            elif isinstance(data, dict) and "generated_text" in data:
                return {"generated_text": data["generated_text"]}

            return {"generated_text": str(data)}

        except httpx.ReadTimeout:
            logger.warning(f"HuggingFace request timed out for model {self.model_id}.")
            return {"generated_text": "Error: HuggingFace request timed out."}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                logger.warning(
                    f"HuggingFace model {self.model_id} is loading. Try again in a moment."
                )
                return {
                    "generated_text": "Model is loading on HuggingFace. Please try again in 30 seconds."
                }
            else:
                logger.error(f"HuggingFace API error for model {self.model_id}: {e}")
                return {"generated_text": f"Error: HuggingFace API error: {e}"}
        except Exception as e:
            logger.error(f"HuggingFace API error for model {self.model_id}: {e}")
            return {
                "generated_text": f"Error: An issue occurred with the HuggingFace API: {e}"
            }

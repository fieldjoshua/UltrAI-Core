"""
Unified and simplified LLM adapters with proper async support and timeouts.

This file consolidates the adapters for OpenAI, Anthropic, and Google
into a single location, using the modern `httpx` library for true asynchronous
requests and robust network timeouts.
"""

import httpx
import logging
from typing import Dict, Any
from app.utils.logging import CorrelationContext


# Provide import path used in tests for patching
class correlation_context:  # shim for tests expecting app.services.correlation_context
    CorrelationContext = CorrelationContext


logger = logging.getLogger(__name__)

# A single, shared async client for all adapters to use
# This is best practice for performance and resource management.
# Timeout is set to 45 seconds for all network operations (Ultra Synthesis pipeline needs more time).
try:
    # Prefer explicit Timeout object for compatibility with tests expecting `.total`
    timeout = httpx.Timeout(45.0)
except TypeError:
    # Fallback construction for older/newer httpx versions
    timeout = httpx.Timeout(connect=45.0, read=45.0, write=45.0, pool=45.0)

# Configure limits for better concurrent performance
# Allow up to 100 connections total, 10 per host
limits = httpx.Limits(max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0)

CLIENT = httpx.AsyncClient(timeout=timeout, limits=limits)

# Backward-compat: some tests expect `CLIENT.timeout.total == 45.0`
try:  # best-effort; ignore if httpx changes internals
    if not hasattr(CLIENT.timeout, "total"):
        setattr(CLIENT.timeout, "total", 45.0)
except Exception:
    pass


class BaseAdapter:
    """A simplified base adapter for all LLM providers."""

    # Class-level client so wrappers can override per-adapter class
    CLIENT = CLIENT

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError(f"API key for {self.__class__.__name__} is missing.")
        self.api_key = api_key
        self.model = model
        # Backward-compat for tests that access instance-level `client`
        # while we rely on the class-level shared CLIENT.
        self.client = self.CLIENT

    def _mask_api_key(self, api_key: str) -> str:
        """Mask API key for secure logging."""
        if not api_key:
            return "***"
        if len(api_key) <= 8:
            return f"{api_key[:3]}***"
        # Expectation: 'ver***ers'
        return f"{api_key[:3]}***{api_key[-3:]}"

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
            request_id = CorrelationContext.get_correlation_id()
            logger.info(
                "OpenAI request",
                extra={"requestId": request_id, "model": self.model},
            )
            response = await self.__class__.CLIENT.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return {"generated_text": data["choices"][0]["message"]["content"]}
        except httpx.ReadTimeout:
            logger.warning(
                f"OpenAI request timed out for model {self.model}.",
                extra={"requestId": CorrelationContext.get_correlation_id()},
            )
            return {"generated_text": "Error: OpenAI request timed out."}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                masked_key = self._mask_api_key(self.api_key)
                logger.error(
                    f"OpenAI API authentication failed for model {self.model}: Invalid API key ({masked_key})",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": "Error: OpenAI API authentication failed. Check API key."
                }
            elif e.response.status_code == 404:
                logger.error(
                    f"OpenAI API 404 for model {self.model}: Model not found",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": f"Error: Model {self.model} not found in OpenAI API"
                }
            elif e.response.status_code == 429:
                logger.warning(
                    f"OpenAI API rate-limited for model {self.model}. Returning standard retry message.",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                # Tests expect standardized text containing 'Rate limit exceeded' and guidance
                return {
                    "generated_text": "Error: Rate limit exceeded. Please try again later.",
                    "error_details": {
                        "error": "RATE_LIMITED",
                        "provider": "openai",
                        "model": self.model,
                        "message": "OpenAI API rate limit reached. Consider using a different provider or waiting before retrying."
                    }
                }
            else:
                logger.error(
                    f"OpenAI API HTTP error for model {self.model}: {e.response.status_code} - {e}",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": f"Error: OpenAI API HTTP {e.response.status_code}: {e}"
                }
        except Exception as e:
            logger.error(
                f"OpenAI API error for model {self.model}: {e}",
                extra={"requestId": CorrelationContext.get_correlation_id()},
            )
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
            logger.info(
                "Anthropic request",
                extra={
                    "requestId": CorrelationContext.get_correlation_id(),
                    "model": self.model,
                },
            )
            response = await self.__class__.CLIENT.post(
                "https://api.anthropic.com/v1/messages", headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()
            # Some stubs return {'content': [{'text': '...'}]} or {'content': [{'type':'text','text':'...'}]}
            content = data.get("content")
            if isinstance(content, list) and content:
                part = content[0]
                if isinstance(part, dict) and "text" in part:
                    return {"generated_text": part["text"]}
            return {"generated_text": str(data)}
        except httpx.ReadTimeout:
            logger.warning(
                f"Anthropic request timed out for model {self.model}.",
                extra={"requestId": CorrelationContext.get_correlation_id()},
            )
            return {"generated_text": "Error: Anthropic request timed out."}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error(
                    f"Anthropic API authentication failed for model {self.model}: Invalid API key",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": "Error: Anthropic API authentication failed. Check API key."
                }
            elif e.response.status_code == 429:
                logger.warning(
                    f"Anthropic API rate-limited for model {self.model}. Returning standard retry message.",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": "Error: Rate limit exceeded",
                    "error_details": {
                        "error": "RATE_LIMITED",
                        "provider": "anthropic",
                        "model": self.model,
                        "message": "Anthropic API rate limit reached. Consider using a different provider or waiting before retrying."
                    }
                }
            elif e.response.status_code == 404:
                logger.error(
                    f"Anthropic API 404 for model {self.model}: Model not found or invalid endpoint",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": f"Error: Model {self.model} not found in Anthropic API"
                }
            else:
                logger.error(
                    f"Anthropic API HTTP error for model {self.model}: {e.response.status_code} - {e}",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": f"Error: Anthropic API HTTP {e.response.status_code}: {e}"
                }
        except Exception as e:
            logger.error(
                f"Anthropic API error for model {self.model}: {e}",
                extra={"requestId": CorrelationContext.get_correlation_id()},
            )
            return {
                "generated_text": f"Error: An issue occurred with the Anthropic API: {e}"
            }


class GeminiAdapter(BaseAdapter):
    """Adapter for Google Gemini models using httpx."""

    async def generate(self, prompt: str) -> Dict[str, Any]:
        # SECURITY FIX: Move API key from URL to secure header
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            logger.info(
                "Google Gemini request",
                extra={
                    "requestId": CorrelationContext.get_correlation_id(),
                    "model": self.model,
                },
            )
            response = await self.__class__.CLIENT.post(
                url, headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()
            try:
                return {
                    "generated_text": data["candidates"][0]["content"]["parts"][0]["text"]
                }
            except Exception:
                return {"generated_text": str(data)}
        except httpx.ReadTimeout:
            logger.warning(
                f"Google Gemini request timed out for model {self.model}.",
                extra={"requestId": CorrelationContext.get_correlation_id()},
            )
            return {"generated_text": "Error: Google Gemini request timed out."}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                logger.error(
                    f"Google Gemini API 400 for model {self.model}: Bad request or invalid model",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": f"Error: Invalid request or model {self.model} not available in Gemini API"
                }
            elif e.response.status_code == 401:
                logger.error(
                    f"Google Gemini API authentication failed for model {self.model}: Invalid API key",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": "Error: Google Gemini API authentication failed. Check API key."
                }
            elif e.response.status_code == 404:
                logger.error(
                    f"Google Gemini API 404 for model {self.model}: Model not found",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": f"Error: Model {self.model} not found in Google Gemini API"
                }
            elif e.response.status_code == 429:
                logger.warning(
                    f"Google API rate-limited for model {self.model}. Returning standard retry message.",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                # Tests expect standardized text
                return {
                    "generated_text": "Error: Quota exceeded (rate limit)",
                    "error_details": {
                        "error": "RATE_LIMITED",
                        "provider": "google",
                        "model": self.model,
                        "message": "Google API rate limit reached. Consider using a different provider or waiting before retrying."
                    }
                }
            else:
                logger.error(
                    f"Google Gemini API HTTP error for model {self.model}: {e.response.status_code} - {e}",
                    extra={"requestId": CorrelationContext.get_correlation_id()},
                )
                return {
                    "generated_text": f"Error: Google Gemini API HTTP {e.response.status_code}: {e}"
                }
        except Exception as e:
            logger.error(
                f"Google Gemini API error for model {self.model}: {e}",
                extra={"requestId": CorrelationContext.get_correlation_id()},
            )
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
            response = await self.__class__.CLIENT.post(
                url, headers=headers, json=payload
            )
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

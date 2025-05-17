"""
Stub implementation of LLM adapter classes.

This file provides stub implementations of LLM adapters so that the system can
run in mock mode without the actual adapter implementations. It's used when the
actual adapter implementations are not available, such as when running in mock mode
or when the relevant libraries are not installed.
"""

import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)
logger.warning(
    "Using stub LLM adapter classes. Actual LLM services will not be available."
)


class BaseAdapter:
    """Base class for LLM adapters"""

    def __init__(self, api_key: str, model: str = None, **kwargs):
        """Initialize the adapter"""
        self.api_key = api_key
        self.model = model or "default-model"
        self.capabilities = self.get_capabilities()

    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of this model"""
        return {
            "supports_streaming": True,
            "max_tokens": 4096,
            "supports_tools": False,
            "name": self.model,
        }

    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a completion for the given prompt"""
        return {
            "generated_text": f"[Mock response from {self.model}]: This is a stub implementation responding to: {prompt[:50]}...",
            "model": self.model,
            "usage": {
                "prompt_tokens": len(prompt),
                "completion_tokens": 50,
                "total_tokens": len(prompt) + 50,
            },
        }

    async def stream(self, prompt: str, **kwargs):
        """Stream a completion for the given prompt"""
        yield {
            "generated_text": f"[Mock streaming response from {self.model}]: ",
            "model": self.model,
            "usage": {
                "prompt_tokens": len(prompt),
                "completion_tokens": 5,
                "total_tokens": len(prompt) + 5,
            },
            "finish_reason": "start",
        }
        yield {
            "generated_text": "This is a stub implementation ",
            "model": self.model,
            "usage": {"prompt_tokens": 0, "completion_tokens": 5, "total_tokens": 5},
            "finish_reason": None,
        }
        yield {
            "generated_text": f"responding to: {prompt[:30]}...",
            "model": self.model,
            "usage": {"prompt_tokens": 0, "completion_tokens": 5, "total_tokens": 5},
            "finish_reason": "stop",
        }


class OpenAIAdapter(BaseAdapter):
    """Stub implementation of OpenAI adapter"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo", **kwargs):
        super().__init__(api_key, model, **kwargs)

    def get_capabilities(self) -> Dict[str, Any]:
        capabilities = super().get_capabilities()
        capabilities["supports_tools"] = True
        if "gpt-4" in self.model:
            capabilities["max_tokens"] = 8192
        return capabilities


class AnthropicAdapter(BaseAdapter):
    """Stub implementation of Anthropic adapter"""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet", **kwargs):
        super().__init__(api_key, model, **kwargs)

    def get_capabilities(self) -> Dict[str, Any]:
        capabilities = super().get_capabilities()
        if "opus" in self.model:
            capabilities["max_tokens"] = 100000
        else:
            capabilities["max_tokens"] = 50000
        return capabilities


class GeminiAdapter(BaseAdapter):
    """Stub implementation of Google Gemini adapter"""

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro", **kwargs):
        super().__init__(api_key, model, **kwargs)

    def get_capabilities(self) -> Dict[str, Any]:
        capabilities = super().get_capabilities()
        if "pro" in self.model:
            capabilities["max_tokens"] = 32768
        else:
            capabilities["max_tokens"] = 16384
        return capabilities

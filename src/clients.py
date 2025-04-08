import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict

import aiohttp

from .config import ModelConfig


class BaseModelClient(ABC):
    def __init__(self, config: ModelConfig):
        self.config = config
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass


class ChatGPTClient(BaseModelClient):
    async def generate(self, prompt: str) -> str:
        async with self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            },
            timeout=self.config.timeout,
        ) as response:
            data = await response.json()
            return data["choices"][0]["message"]["content"]


class GeminiClient(BaseModelClient):
    async def generate(self, prompt: str) -> str:
        async with self.session.post(
            f"{self.config.base_url}/v1/models/gemini-pro:generateContent",
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxTokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                },
            },
            timeout=self.config.timeout,
        ) as response:
            data = await response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


class LlamaClient(BaseModelClient):
    async def generate(self, prompt: str) -> str:
        async with self.session.post(
            f"{self.config.base_url}/generate",
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            json={
                "prompt": prompt,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            },
            timeout=self.config.timeout,
        ) as response:
            data = await response.json()
            return data["generated_text"]

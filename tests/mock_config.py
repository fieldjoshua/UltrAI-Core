"""
Mock configurations for different test modes.

This module provides reusable mock objects and responses
for consistent testing across the Ultra test suite.
"""

from unittest.mock import AsyncMock, Mock
from typing import Dict, Any, Optional
import json


class MockLLMResponses:
    """Predefined responses for mock LLMs."""
    
    SIMPLE_RESPONSE = {
        "generated_text": "This is a simple test response from the mock LLM.",
        "provider": "mock",
        "model": "mock-model"
    }
    
    SIMPLE = "This is a simple test response from the mock LLM."
    
    MACHINE_LEARNING = """Machine learning is a subset of artificial intelligence 
    that enables systems to learn and improve from experience without being 
    explicitly programmed. It focuses on developing algorithms that can analyze 
    data, identify patterns, and make decisions with minimal human intervention."""
    
    ERROR_RESPONSE = "Error: Mock error response for testing error handling."
    
    SYNTHESIS = """Based on comprehensive analysis of the provided information,
    here is a synthesized response that combines insights from multiple sources
    and provides a unified perspective on the topic."""
    
    @staticmethod
    def get_response(query: str, mode: str = "simple") -> str:
        """Get appropriate mock response based on query and mode."""
        query_lower = query.lower()
        
        if "error" in query_lower:
            return MockLLMResponses.ERROR_RESPONSE
        elif "machine learning" in query_lower or "ml" in query_lower:
            return MockLLMResponses.MACHINE_LEARNING
        elif mode == "synthesis":
            return MockLLMResponses.SYNTHESIS
        else:
            return MockLLMResponses.SIMPLE


class MockLLMAdapter:
    """Mock LLM adapter for testing."""
    
    def __init__(self, model_name: str, response_mode: str = "simple"):
        self.model = model_name
        self.response_mode = response_mode
        self.call_count = 0
        self.last_prompt = None
        
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Mock generate method."""
        self.call_count += 1
        self.last_prompt = prompt
        
        response = MockLLMResponses.get_response(prompt, self.response_mode)
        
        return {
            "generated_text": response,
            "model": self.model,
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(prompt.split()) + len(response.split())
            }
        }


def create_mock_openai_adapter():
    """Create a mock OpenAI adapter."""
    mock = Mock()
    mock.generate = AsyncMock(side_effect=MockLLMAdapter("gpt-4").generate)
    return mock


def create_mock_anthropic_adapter():
    """Create a mock Anthropic adapter."""
    mock = Mock()
    mock.generate = AsyncMock(side_effect=MockLLMAdapter("claude-3-opus").generate)
    return mock


def create_mock_llm_adapter(provider: str, model: str):
    """Create a generic mock LLM adapter."""
    adapter = MockLLMAdapter(model)
    adapter.provider = provider
    
    # Store the original generate method
    original_generate = adapter.generate
    
    async def generate_with_provider(prompt: str) -> Dict[str, Any]:
        # Call the original generate method
        result = await original_generate(prompt)
        result["provider"] = provider
        result["generated_text"] = f"Mock {provider} response for prompt: {prompt[:50]}..."
        return result
    
    adapter.generate = generate_with_provider
    return adapter


def create_mock_gemini_adapter():
    """Create a mock Gemini adapter."""
    mock = Mock()
    mock.generate = AsyncMock(side_effect=MockLLMAdapter("gemini-pro").generate)
    return mock


def create_mock_huggingface_adapter():
    """Create a mock HuggingFace adapter."""
    mock = Mock()
    mock.generate = AsyncMock(side_effect=MockLLMAdapter("mistralai/Mistral-7B").generate)
    return mock


class MockRedisClient:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.data = {}
        self.call_count = 0
        
    async def get(self, key: str) -> Optional[bytes]:
        """Mock get method."""
        self.call_count += 1
        value = self.data.get(key)
        return value.encode() if isinstance(value, str) else value
        
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        """Mock set method."""
        self.call_count += 1
        self.data[key] = value
        
    async def delete(self, key: str) -> None:
        """Mock delete method."""
        self.call_count += 1
        self.data.pop(key, None)
        
    async def keys(self, pattern: str = "*") -> list[str]:
        """Mock keys method."""
        import fnmatch
        return [k for k in self.data.keys() if fnmatch.fnmatch(k, pattern)]
        
    async def ping(self) -> bool:
        """Mock ping method."""
        return True
        
    async def close(self) -> None:
        """Mock close method."""
        pass


class MockCacheService:
    """Mock cache service for testing."""
    
    def __init__(self, use_redis: bool = False):
        self.redis = MockRedisClient() if use_redis else None
        self.memory_cache = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "memory_fallbacks": 0
        }
        
    async def aget(self, key: str) -> Optional[Any]:
        """Mock async get."""
        if key in self.memory_cache:
            self._stats["hits"] += 1
            return self.memory_cache[key]
        self._stats["misses"] += 1
        return None
        
    async def aset(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Mock async set."""
        self.memory_cache[key] = value
        
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return self._stats.copy()


class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self):
        self.users = {}
        self.transactions = []
        self.analyses = []
        
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Mock get user."""
        return self.users.get(user_id)
        
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock create user."""
        user_id = user_data.get("id", f"user_{len(self.users)}")
        self.users[user_id] = user_data
        return user_data
        
    async def add_transaction(self, transaction: Dict[str, Any]) -> None:
        """Mock add transaction."""
        self.transactions.append(transaction)
        
    async def get_transactions(self, user_id: str) -> list[Dict[str, Any]]:
        """Mock get transactions."""
        return [t for t in self.transactions if t.get("user_id") == user_id]


def create_mock_http_client():
    """Create a mock HTTP client for testing."""
    mock_client = AsyncMock()
    
    # Default successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_response.text = "Success"
    mock_response.headers = {}
    
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    mock_client.put.return_value = mock_response
    mock_client.delete.return_value = mock_response
    
    return mock_client


# Factory functions for creating configured mocks based on test mode
def get_mock_llm_adapters(test_mode: str = "simple"):
    """Get configured mock LLM adapters."""
    return {
        "openai": create_mock_openai_adapter(),
        "anthropic": create_mock_anthropic_adapter(),
        "gemini": create_mock_gemini_adapter(),
        "huggingface": create_mock_huggingface_adapter()
    }


def get_mock_services(test_mode: str = "simple"):
    """Get configured mock services."""
    return {
        "cache": MockCacheService(),
        "database": MockDatabase(),
        "http_client": create_mock_http_client()
    }
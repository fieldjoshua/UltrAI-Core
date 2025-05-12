# LLM Adapters

This directory contains adapter implementations for different LLM providers.

## Overview

Adapters serve as the interface between the orchestration system and specific LLM providers. Each adapter implements a common interface defined in `base_adapter.py` but handles provider-specific details.

## Components

- `base_adapter.py` - Abstract base class that defines the adapter interface
- `adapter_factory.py` - Factory for creating appropriate adapters
- `mock_adapter.py` - Mock implementation for testing and development
- `simple_mock_adapter.py` - Simplified mock adapter for Docker environment
- Provider-specific adapters:
  - `openai_adapter.py` - OpenAI's GPT models
  - `anthropic_adapter.py` - Anthropic's Claude models
  - `google_adapter.py` - Google's Gemini models
  - `cohere_adapter.py` - Cohere models
  - `mistral_adapter.py` - Mistral models
  - `custom_adapter.py` - Template for custom implementations

## Usage in Docker

When running in Docker, adapters require API keys to be set in the environment.
See the `.env.example` file for the required environment variables:

```
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here
```

To use adapters without mocks:

```bash
# Set USE_MOCK to false
USE_MOCK=false ./scripts/run-docker-orchestrator.sh
```

## Adding a New Adapter

To add support for a new LLM provider:

1. Create a new adapter class that inherits from `BaseAdapter`
2. Implement all required methods
3. Add the adapter to the factory in `adapter_factory.py`

Example:

```python
from src.adapters.base_adapter import BaseAdapter
from src.orchestration.config import ModelConfig

class NewProviderAdapter(BaseAdapter):
    def __init__(self, model_config: ModelConfig):
        super().__init__(model_config)
        # Initialize provider-specific client
        
    async def generate(self, prompt, **kwargs):
        # Implement provider-specific generation
        
    async def get_embedding(self, text, **kwargs):
        # Implement provider-specific embedding
        
    def is_available(self):
        # Check if provider is available
```

Then add it to the factory:

```python
# In adapter_factory.py
elif provider == LLMProvider.NEW_PROVIDER:
    from src.adapters.new_provider_adapter import NewProviderAdapter
    return NewProviderAdapter(model_config)
```

## Model Naming Convention

Models are specified using a provider-model format:

- `openai-gpt4o`: OpenAI's GPT-4o model
- `anthropic-claude`: Anthropic's Claude model
- `google-gemini`: Google's Gemini model
- `mock-llm`: Mock LLM for testing

## Error Handling

Adapters include robust error handling for:

- API authentication errors
- Rate limiting
- Timeouts
- Invalid requests

Errors are logged and can be caught by client code.
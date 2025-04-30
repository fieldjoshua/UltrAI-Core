# LLM Integration Guide for Ultra

This guide documents how to integrate with various Language Model providers in the Ultra system.

## Supported LLM Providers

Ultra currently supports the following LLM providers:

1. OpenAI (GPT models)
2. Anthropic (Claude models)
3. Google (Gemini models)
4. Local models via Ollama

## API Client Architecture

Each LLM provider has a dedicated client class that implements a common interface:

```python
class BaseLLMClient:
    async def generate_response(self, prompt: str, options: dict = None) -> dict:
        """Generate a response for the given prompt"""
        raise NotImplementedError("Subclasses must implement this method")

    async def get_available_models(self) -> list:
        """Get a list of available models for this provider"""
        raise NotImplementedError("Subclasses must implement this method")
```

## Integration Requirements

### API Keys

API keys are required for each external LLM provider. These are configured in the `.env` file:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIza-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Configuration Options

Provider-specific configuration options can be set in the `.env` file:

```
OPENAI_ORG_ID=org-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_VERSION=2023-06-01
GOOGLE_PROJECT_ID=your-project-id
```

## Adding a New Provider

To add support for a new LLM provider:

1. Create a new client class that inherits from `BaseLLMClient`
2. Implement the required methods
3. Register the client in the `LLMClientFactory`

### Example: Adding a New Provider

```python
from .base import BaseLLMClient

class NewProviderClient(BaseLLMClient):
    def __init__(self, api_key, **kwargs):
        self.api_key = api_key
        self.client = SomeProviderSDK(api_key=api_key)
        self.default_options = kwargs.get("default_options", {})

    async def generate_response(self, prompt: str, options: dict = None) -> dict:
        merged_options = {**self.default_options, **(options or {})}

        try:
            response = await self.client.completions.create(
                prompt=prompt,
                **merged_options
            )

            return {
                "text": response.text,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "finish_reason": response.finish_reason
            }
        except Exception as e:
            return {
                "error": str(e),
                "text": None
            }

    async def get_available_models(self) -> list:
        try:
            models = await self.client.models.list()
            return [model.id for model in models]
        except Exception as e:
            return []
```

## Request/Response Format

All LLM client responses follow a standard format:

```json
{
  "text": "The generated response text",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 150,
    "total_tokens": 160
  },
  "model": "gpt-4",
  "finish_reason": "stop",
  "error": null
}
```

If an error occurs, the response will contain an error field:

```json
{
  "text": null,
  "error": "Error message from the provider",
  "model": "gpt-4"
}
```

## Error Handling

The LLM integration system implements the following error handling strategies:

1. **Retries**: Automatic retries for transient errors like rate limits and timeouts
2. **Fallbacks**: Optional fallback to alternative models when primary model fails
3. **Timeout Protection**: Configurable timeouts to prevent hanging requests
4. **Circuit Breaking**: Circuit breaker pattern to avoid overwhelming failing services

## Using the Mock LLM Service

For development and testing without API keys, Ultra provides a mock LLM service:

```python
from services.mock_llm_service import MockLLMService

mock_service = MockLLMService()
response = await mock_service.analyze_prompt(
    prompt="What is the meaning of life?",
    models=["gpt4o", "claude37"],
    ultra_model="gpt4o",
    pattern="confidence"
)
```

Enable the mock service in your `.env` file:

```
ENABLE_MOCK_LLM=true
```

## Integration Testing

Use the `llm_integration_test.py` script to test your LLM integrations:

```bash
python llm_integration_test.py --test-all
```

Or test specific providers:

```bash
python llm_integration_test.py --test-provider openai
```

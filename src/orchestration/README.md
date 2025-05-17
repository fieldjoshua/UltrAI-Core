# UltraAI Orchestration System

The orchestration module provides a modular, extensible system for coordinating multiple LLM providers, processing requests in parallel, handling errors and retries, and synthesizing responses.

## Architecture

The orchestration system follows a modular architecture with the following components:

- **BaseOrchestrator**: Abstract base class providing core functionality like provider registration, request handling, error management, and statistics tracking.
- **SimpleOrchestrator**: Basic implementation focused on collecting responses, analyzing them, and synthesizing a final response.
- **ParallelOrchestrator**: Performance-focused implementation with dynamic provider prioritization and early stopping capabilities.
- **AdaptiveOrchestrator**: Advanced implementation that adapts its strategy based on the request context, system load, and historical performance.

## Components

- `config.py` - Configuration classes for orchestrators and models
- `base_orchestrator.py` - Abstract base orchestrator implementation
- `simple_orchestrator.py` - Basic orchestrator with analysis and synthesis
- `parallel_orchestrator.py` - Performance-optimized orchestrator with early stopping
- `adaptive_orchestrator.py` - Context-aware orchestrator with strategy selection

## Features

- **Provider Management**: Dynamic registration and configuration of LLM providers
- **Parallel Processing**: Efficient handling of multiple LLM requests in parallel
- **Error Handling**: Robust error handling with configurable retry policies
- **Fallback Mechanisms**: Graceful degradation with provider fallback chains
- **Response Synthesis**: Integration of multiple LLM responses into a coherent output
- **Performance Monitoring**: Detailed statistics tracking for optimization
- **Mock Mode Support**: Development support without requiring actual API keys
- **Adaptive Strategies**: Context-aware orchestration strategy selection

## Usage

### Basic Usage

```python
import asyncio
from src.orchestration import SimpleOrchestrator

async def main():
    # Initialize the orchestrator
    orchestrator = SimpleOrchestrator(
        max_retries=3,
        parallel_requests=True,
        analysis_type="comparative"
    )

    # Register providers
    await orchestrator.register_provider(
        provider_id="openai",
        provider_type="openai",
        api_key="YOUR_OPENAI_API_KEY",
        model="gpt-4o"
    )

    await orchestrator.register_provider(
        provider_id="anthropic",
        provider_type="anthropic",
        api_key="YOUR_ANTHROPIC_API_KEY",
        model="claude-3-opus-20240229"
    )

    # Process a prompt
    result = await orchestrator.process(
        "Explain the benefits of multi-LLM orchestration systems."
    )

    # Access the synthesized response
    synthesis = result["synthesis"]["response"]
    print(synthesis)

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage

See `examples/orchestrator_example.py` for more detailed usage examples, including:

- Using different orchestrator types for different use cases
- Working with various orchestration strategies
- Handling provider selection and prioritization
- Processing and analyzing responses

## Configuration

The orchestration system is highly configurable through both constructor parameters and runtime options. Key configuration options include:

- **max_retries**: Maximum number of retries for failed requests
- **parallel_requests**: Whether to process LLM requests in parallel
- **timeout_seconds**: Timeout for LLM requests in seconds
- **analysis_type**: Type of analysis to perform (comparative, factual)
- **use_early_stopping**: Whether to stop processing when sufficient quality responses are received
- **min_responses_needed**: Minimum number of successful responses needed before synthesis
- **max_providers_per_request**: Maximum number of providers to use per request

## Extending the System

The orchestration system is designed to be extended with custom orchestrator implementations. To create a custom orchestrator:

1. Inherit from `BaseOrchestrator`
2. Implement the required `process()` method
3. Add any additional specialized functionality
4. Register the orchestrator in the module's `__init__.py`

```python
from src.orchestration import BaseOrchestrator

class CustomOrchestrator(BaseOrchestrator):
    """Custom orchestrator implementation."""

    async def process(self, prompt: str, **options):
        """Implement your custom orchestration logic here."""
        # Custom logic...
        pass
```

## Future Enhancements

Planned enhancements for the orchestration system include:

- Learning-based provider selection based on prompt characteristics
- Tool-augmented orchestration for complex tasks
- Context-aware prompt optimization
- Response quality evaluation metrics
- Advanced caching strategies
- Support for streaming responses
- Document/image processing support

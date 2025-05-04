# Simple Core Orchestrator

This directory contains a simplified core implementation of the LLM orchestration system. It provides the most direct path from request to response with minimal abstractions.

## Design Principles

- **Simplicity**: Minimize abstractions and complexity
- **Directness**: Provide the most direct path from request to response
- **Efficiency**: Optimize for both performance and code maintainability
- **Extensibility**: Allow for easy extension without modifying core code

## Components

### Basic Orchestration (Iteration 1)

- `config.py`: Simple configuration structure
- `adapter.py`: Adapter interface with implementations for OpenAI, Anthropic, Gemini, and Llama
- `orchestrator.py`: Streamlined orchestrator with parallel execution
- `factory.py`: Factory functions for creating orchestrators

### Enhanced Orchestration (Iteration 2)

- `enhanced_orchestrator.py`: Multi-stage orchestrator with meta-analysis and synthesis
- `prompt_templates.py`: Templates for different processing stages
- `quality_metrics.py`: Metrics for evaluating and ranking responses
- `cache_service.py`: Simple caching mechanism for responses

## Usage

### Basic Orchestrator

```python
from src.simple_core.factory import create_orchestrator
from src.simple_core.config import Config, ModelDefinition

# Create configuration
config = Config(
    models=[
        ModelDefinition(name="openai-gpt4", provider="openai", priority=1,
                       options={"model_id": "gpt-4o"}),
        ModelDefinition(name="anthropic-claude", provider="anthropic", priority=2,
                       options={"model_id": "claude-3-opus-20240229"})
    ],
    parallel=True
)

# Create basic orchestrator
orchestrator = create_orchestrator(config)

# Process request
response = await orchestrator.process({
    "prompt": "What is an LLM orchestrator?"
})

# Access results
print(response["primary"]["response"])  # Primary response content
```

### Enhanced Orchestrator (Multi-stage)

```python
from src.simple_core.factory import create_orchestrator
from src.simple_core.config import Config, ModelDefinition

# Create configuration
config = Config(
    models=[
        ModelDefinition(name="openai-gpt4", provider="openai", priority=1,
                       options={"model_id": "gpt-4o"}),
        ModelDefinition(name="anthropic-claude", provider="anthropic", priority=2,
                       options={"model_id": "claude-3-opus-20240229"})
    ],
    parallel=True
)

# Create enhanced orchestrator
orchestrator = create_orchestrator(config, enhanced=True)

# Process request
result = await orchestrator.process({
    "prompt": "What is an LLM orchestrator?"
})

# Access different levels of results
print("Initial Responses:")
for resp in result["initial_responses"]:
    print(f"{resp['model']}: {resp['response'][:100]}...")

print("\nMeta-Analyses:")
for analysis in result["meta_analyses"]:
    print(f"{analysis['model']}: {analysis['analysis'][:100]}...")

print("\nSynthesized Response:")
print(result["synthesis"]["response"])

print("\nBest Individual Response:")
print(f"{result['selected_response']['model']}: {result['selected_response']['response'][:100]}...")
```

### Quick Setup from Environment

The simplest way to get started is to use the environment-based setup:

```python
import asyncio
from src.simple_core.factory import create_from_env

# Set environment variables first:
# export OPENAI_API_KEY="your_key"
# export ANTHROPIC_API_KEY="your_key"
# export GOOGLE_API_KEY="your_key"

async def run_example():
    # Create basic orchestrator from environment
    orchestrator = create_from_env()

    # Or create enhanced orchestrator
    # orchestrator = create_from_env(enhanced=True)

    if orchestrator:
        result = await orchestrator.process({"prompt": "What is an LLM orchestrator?"})
        print(result)

asyncio.run(run_example())
```

## Interactive Examples

For interactive testing, try the example scripts:

- `examples/interactive.py`: Basic orchestrator interactive session
- `examples/enhanced_interactive.py`: Enhanced orchestrator with meta-analysis and synthesis

## Next Steps

Potential future enhancements:

- Advanced quality metrics with model-based evaluation
- Response streaming support
- More sophisticated caching mechanisms
- Context management for multi-turn conversations

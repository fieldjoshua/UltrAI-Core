# Ultra LLM Orchestrator Guide

This guide explains how to use the enhanced `MultiLLMOrchestrator` to integrate and orchestrate multiple language models in your application.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Model Registration and Weights](#model-registration-and-weights)
3. [Processing Pipeline](#processing-pipeline)
4. [Error Handling and Retries](#error-handling-and-retries)
5. [Caching Responses](#caching-responses)
6. [Performance Metrics](#performance-metrics)
7. [Advanced Customization](#advanced-customization)

## Basic Usage

The `MultiLLMOrchestrator` allows you to integrate multiple language models and process responses using a flexible pipeline.

```python
from src.orchestrator import MultiLLMOrchestrator
from my_llm_clients import llama_client, chatgpt_client, gemini_client

# Initialize the orchestrator
orchestrator = MultiLLMOrchestrator()

# Register your LLM clients
orchestrator.register_model('llama', llama_client)
orchestrator.register_model('chatgpt', chatgpt_client)
orchestrator.register_model('gemini', gemini_client)

# Process a prompt
results = await orchestrator.process_responses("Your prompt here")

# Access the results
initial_responses = results["initial_responses"]
meta_responses = results["meta_responses"]
final_synthesis = results["final_synthesis"]
```

## Model Registration and Weights

### Registering Models with Weights

Models can be registered with weights that determine their priority in the orchestration process:

```python
# Register models with weights (higher weight = higher priority)
orchestrator.register_model('llama', llama_client, weight=1.0)
orchestrator.register_model('chatgpt', chatgpt_client, weight=3.0)
orchestrator.register_model('gemini', gemini_client, weight=2.0)
```

### Updating Model Weights

You can update model weights dynamically:

```python
# Update a model's weight
orchestrator.set_model_weight('llama', 4.0)
```

### Getting Prioritized Models

Get a list of models sorted by their priority:

```python
# Get all models in priority order
prioritized_models = orchestrator.get_prioritized_models()

# Get specific models in priority order
specific_models = orchestrator.get_prioritized_models(['llama', 'gemini'])
```

## Processing Pipeline

### Pipeline Stages

The orchestrator uses a flexible pipeline with the following stages:

1. **Initial**: Get responses from all models for the original prompt
2. **Meta**: Analyze the initial responses to identify key insights
3. **Synthesis**: Create a comprehensive synthesis of all responses

### Customizing Pipeline Stages

You can specify which stages to run:

```python
# Run only initial and synthesis stages
results = await orchestrator.process_responses(
    prompt="Your prompt here",
    stages=["initial", "synthesis"]
)
```

### Selecting Specific Models

You can specify which models to use in the pipeline:

```python
# Use only specific models
results = await orchestrator.process_responses(
    prompt="Your prompt here",
    models=["llama", "chatgpt"]
)
```

## Error Handling and Retries

The orchestrator includes robust error handling and automatic retries:

```python
# Customize retry behavior
orchestrator = MultiLLMOrchestrator(max_retries=5)
```

When a model fails, the orchestrator will:

1. Log the error
2. Retry the request up to `max_retries` times
3. If all retries fail, it will log a critical error and raise an exception

## Caching Responses

Response caching is enabled by default to improve performance:

```python
# Disable caching
orchestrator = MultiLLMOrchestrator(cache_enabled=False)

# Use cache in get_model_response
response = await orchestrator.get_model_response(
    model=llama_client,
    prompt="Your prompt",
    stage="initial",
    use_cache=True  # Set to False to bypass cache
)
```

## Performance Metrics

The orchestrator automatically tracks performance metrics for each model:

```python
# Get metrics after processing responses
metrics = results["metrics"]
```

Metrics include:

- Response times
- Success rates
- Token usage
- Quality scores

## Advanced Customization

### Extending the Orchestrator

To add new orchestration strategies, subclass `MultiLLMOrchestrator` and override `process_responses`:

```python
class CustomOrchestrator(MultiLLMOrchestrator):
    async def process_responses(self, prompt, stages=None, models=None):
        # Custom implementation
        ...
```

### Creating Custom Pipeline Stages

You can create custom pipeline stages by adding new prompt creation methods:

```python
class CustomOrchestrator(MultiLLMOrchestrator):
    def _create_custom_prompt(self, responses):
        # Create a custom prompt
        ...
```

---

For more details, see the docstrings in the `orchestrator.py` file and the test examples in `test_orchestrator.py`.

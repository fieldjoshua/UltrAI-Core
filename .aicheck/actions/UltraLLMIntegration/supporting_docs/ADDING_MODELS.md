# How to Add New LLMs to the Ultra Orchestrator

## 1. Registering a New Model

In your application code, after instantiating the orchestrator:

```python
from src.orchestrator import MultiLLMOrchestrator

orchestrator = MultiLLMOrchestrator()

# Register your LLM clients with optional weights
orchestrator.register_model('llama', llama_client, weight=1.0)
orchestrator.register_model('chatgpt', chatgpt_client, weight=3.0)
orchestrator.register_model('gemini', gemini_client, weight=2.0)
# Add more as needed:
orchestrator.register_model('my_new_model', my_new_model_client, weight=1.5)
```

- The `name` should be a unique string identifier for the model.
- The `client` should implement a `.generate(prompt)` async method returning the model's response.
- The `weight` (optional) determines the priority of the model in the pipeline. Higher weights give higher priority.

## 2. Customizing the Orchestration Pipeline

You can specify which stages to run, in what order, and which models to use:

```python
results = await orchestrator.process_responses(
    prompt="Your prompt here",
    stages=["initial", "meta", "synthesis"],  # or customize as needed
    models=["chatgpt", "gemini"]  # or use all models by default
)
```

- The pipeline is flexible: you can add or remove stages as your workflow evolves.
- By default, the orchestrator will run "initial", "meta", and "synthesis" stages with all registered models.
- Specify `models` to use only a subset of registered models.

## 3. Updating Model Weights

You can update model weights dynamically to adjust priorities:

```python
# Increase the importance of a specific model
orchestrator.set_model_weight('llama', 4.0)

# Get models sorted by their priority
prioritized_models = orchestrator.get_prioritized_models()
```

## 4. Extending the Orchestrator

- To add new orchestration strategies, subclass `MultiLLMOrchestrator` and override `process_responses`.
- To add new evaluation or aggregation logic, extend or modify the relevant methods.
- To create custom pipeline stages, add new prompt creation methods.

For a complete guide to the enhanced orchestrator features, see `ORCHESTRATOR_GUIDE.md`.

---
For more, see the orchestrator docstrings and code comments.

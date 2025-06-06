# Models Module

This directory contains the implementation of various model-related components, including the enhanced orchestrator system for managing multiple LLMs.

## Enhanced Orchestrator

The `EnhancedOrchestrator` provides a flexible and robust system for managing multiple LLMs, applying analysis patterns, tracking progress, and implementing fault tolerance.

### Key Features

- **Model Registry**: Standardized integration with different LLM providers through adapters
- **Analysis Patterns**: Support for applying different analysis patterns to prompts
- **Progress Tracking**: Detailed tracking and reporting of processing progress
- **Fault Tolerance**: Circuit breaker pattern to prevent cascading failures
- **Parallel Processing**: Efficient processing of multiple requests in parallel
- **Caching**: Response caching to improve performance and reduce API costs
- **Analysis Modes**: Predefined configurations for different types of analysis
- **Metrics Collection**: Detailed metrics on performance, quality, and usage

### Usage Examples

#### Basic Usage

```python
from src.models.enhanced_orchestrator import EnhancedOrchestrator, OrchestratorConfig

# Create an orchestrator with default config
orchestrator = EnhancedOrchestrator()

# Register models
orchestrator.register_model(
    name="gpt-4",
    api_key="your-openai-key",
    provider="openai",
    model="gpt-4",
    weight=1.0,
)
orchestrator.register_model(
    name="claude",
    api_key="your-anthropic-key",
    provider="anthropic",
    model="claude-3-opus-20240229",
    weight=0.8,
)

# Process a prompt with a specific pattern
result = await orchestrator.process_with_pattern(
    prompt="Analyze the impact of AI on society",
    pattern_name="perspective",  # Use perspective analysis pattern
)

# Get the best response
best_response = orchestrator.get_best_response(result)
print(best_response)
```

#### Using Analysis Modes

```python
# Process with a predefined analysis mode
result = await orchestrator.process_with_analysis_mode(
    prompt="What are the ethical implications of AI in healthcare?",
    mode="thorough",  # Use thorough analysis mode
)

# Quick analysis with best response
response = await orchestrator.quick_analyze(
    prompt="How can we ensure AI is developed responsibly?",
    analysis_type="creative",  # Use creative analysis type
)
print(response)

# Compare different analysis approaches
comparison = await orchestrator.compare_analyses(
    prompt="What are the most promising applications of AI in the next decade?",
    analysis_types=["fast", "thorough", "creative"],
)
```

## Architecture

The enhanced orchestrator system is composed of the following components:

1. **EnhancedOrchestrator**: Main orchestration class that coordinates the entire process
2. **LLMAdapter**: Adapter pattern for different LLM providers
3. **AnalysisPattern**: Configuration for different analysis patterns
4. **ProgressTracker**: Tracking and reporting of processing progress
5. **CircuitBreaker**: Implementation of the circuit breaker pattern for fault tolerance
6. **ResponseCache**: Caching of model responses for improved performance
7. **AnalysisMode**: Configuration for different analysis modes

## Components

### LLM Adapters

The system supports the following LLM providers:

- OpenAI (GPT models)
- Anthropic (Claude models)
- Google (Gemini models)
- Mistral
- Cohere

### Analysis Patterns

The system includes several predefined analysis patterns:

- **Gut Analysis**: Relies on LLM intuition while considering other responses without assuming factual correctness
- **Confidence Analysis**: Analyzes responses with confidence scoring and agreement tracking
- **Critique Analysis**: Implements a structured critique and revision process
- **Fact Check Analysis**: Implements a rigorous fact-checking process
- **Perspective Analysis**: Focuses on different analytical perspectives and their integration
- **Scenario Analysis**: Analyzes responses through different scenarios and conditions
- **Stakeholder Vision**: Analyzes from multiple stakeholder perspectives
- **Systems Mapper**: Maps complex system dynamics with feedback loops and leverage points
- **Time Horizon**: Analyzes across multiple time frames to balance short and long-term considerations
- **Innovation Bridge**: Uses cross-domain analogies to discover non-obvious patterns and solutions

### Analysis Modes

The system includes several predefined analysis modes:

- **Standard**: Uses the default pattern with all models
- **Fast**: Quick analysis with the best model
- **Thorough**: In-depth analysis using all models
- **Creative**: Focuses on creative perspectives with all models

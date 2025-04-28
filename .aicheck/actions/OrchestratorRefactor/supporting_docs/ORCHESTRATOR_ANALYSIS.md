# Orchestrator Analysis and Improvement Plan

## Current State Analysis

The current `MultiLLMOrchestrator` in `src/orchestrator.py` provides a foundation for working with multiple LLMs, but has several limitations that should be addressed to support the functional prototype requirements.

### Strengths

1. **Flexible Model Registration**: The orchestrator allows dynamic registration of models with a weight-based prioritization system.

2. **Multi-Stage Processing**: The system supports a basic pipeline with initial, meta, and synthesis stages.

3. **Response Caching**: Includes caching functionality to avoid redundant API calls.

4. **Retry Logic**: Basic retry mechanism for failed API calls.

5. **Metrics Collection**: Tracks basic performance metrics like response times and success rates.

### Limitations

1. **LLM Integration**:
   - No standardized interface for interacting with different LLM providers
   - Does not leverage the more comprehensive model handling in `ultra_llm.py` and `ultra_model_selector.py`
   - Model registration requires knowing the underlying client implementation details

2. **Analysis Pattern Integration**:
   - No integration with the analysis patterns defined in `ultra_analysis_patterns.py`
   - Limited to hardcoded processing stages rather than configurable analysis patterns
   - Cannot leverage the rich set of templates and instructions in existing patterns

3. **Progress Tracking**:
   - Limited progress tracking for multi-stage analyses
   - No structured way to report progress to clients
   - Difficult to monitor long-running analyses

4. **Error Handling**:
   - Basic error handling without sophisticated recovery mechanisms
   - No circuit breaker pattern to prevent cascading failures
   - Limited logging of failure reasons and contexts

5. **Pipeline Efficiency**:
   - Suboptimal parallel execution strategies
   - No batching of similar requests
   - Fixed pipeline structure limits flexibility

## Improvement Recommendations

### 1. Unified LLM Interface

Create a standardized adapter pattern for LLM integrations:

```python
class LLMAdapter:
    """Base adapter for LLM integrations."""

    async def generate(self, prompt: str, **options) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError

    async def check_availability(self) -> bool:
        """Check if the LLM is available."""
        raise NotImplementedError

    def get_capabilities(self) -> Dict[str, Any]:
        """Get LLM capabilities."""
        raise NotImplementedError
```

Implement adapters for each LLM provider:

```python
class OpenAIAdapter(LLMAdapter):
    """Adapter for OpenAI models."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, prompt: str, **options) -> str:
        """Generate a response from OpenAI."""
        response = await self.client.chat.completions.create(
            model=options.get("model", self.model),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=options.get("max_tokens", 1500),
            temperature=options.get("temperature", 0.7),
        )
        return response.choices[0].message.content
```

### 2. Analysis Pattern Integration

Integrate the existing analysis patterns system:

```python
class PatternBasedOrchestrator(MultiLLMOrchestrator):
    """Enhanced orchestrator with pattern support."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.patterns = get_pattern_mapping()

    async def process_with_pattern(
        self,
        prompt: str,
        pattern_name: str,
        models: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Process a prompt using a specific analysis pattern."""
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        # Use pattern stages instead of hardcoded ones
        return await self.process_responses(
            prompt=prompt,
            stages=pattern.stages,
            models=models,
            pattern=pattern,
        )
```

### 3. Progress Tracking

Implement a comprehensive progress tracking system:

```python
@dataclass
class ProgressUpdate:
    """Progress update for orchestrator operations."""

    stage: str
    progress: float  # 0.0 to 1.0
    message: str
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
```

Add progress callback support:

```python
async def process_responses(
    self,
    prompt: str,
    stages: List[str],
    models: Optional[List[str]] = None,
    progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
) -> Dict[str, Any]:
    """Process with progress updates."""
    # Implementation with progress updates
```

### 4. Circuit Breaker Pattern

Implement a circuit breaker to prevent cascading failures:

```python
class CircuitBreaker:
    """Circuit breaker for API calls."""

    def __init__(self, failure_threshold: int = 5, recovery_time: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failure_count = {}
        self.open_until = {}

    def is_open(self, service: str) -> bool:
        """Check if circuit is open for a service."""
        if service in self.open_until:
            if time.time() > self.open_until[service]:
                # Reset if recovery time has passed
                del self.open_until[service]
                self.failure_count[service] = 0
                return False
            return True
        return False

    def record_failure(self, service: str) -> bool:
        """Record a service failure and check if circuit should open."""
        if service not in self.failure_count:
            self.failure_count[service] = 0

        self.failure_count[service] += 1

        if self.failure_count[service] >= self.failure_threshold:
            self.open_until[service] = time.time() + self.recovery_time
            return True
        return False

    def record_success(self, service: str):
        """Record a successful operation."""
        if service in self.failure_count:
            self.failure_count[service] = 0
```

### 5. Pipeline Optimization

Improve the processing pipeline for better efficiency:

```python
async def process_in_parallel(
    self,
    prompts: List[str],
    model_names: List[str],
    batch_size: int = 3,
) -> List[ModelResponse]:
    """Process multiple prompts in parallel with batching."""
    results = []

    # Process in batches to avoid overwhelming APIs
    for i in range(0, len(prompts), batch_size):
        batch_prompts = prompts[i:i+batch_size]
        batch_tasks = []

        for model_name in model_names:
            for prompt in batch_prompts:
                model = self.models[model_name]
                task = self.get_model_response(model, prompt, "batch")
                batch_tasks.append(task)

        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        valid_results = [r for r in batch_results if isinstance(r, ModelResponse)]
        results.extend(valid_results)

    return results
```

## Implementation Strategy

1. **Phase 1: LLM Integration**
   - Create adapter classes for each LLM provider
   - Standardize the interface for model interaction
   - Integrate with model selector for dynamic LLM selection

2. **Phase 2: Pattern Integration**
   - Connect the orchestrator with analysis patterns
   - Implement stage-specific template processing
   - Support all pattern types in the orchestrator

3. **Phase 3: Progress and Error Handling**
   - Implement the progress tracking system
   - Add the circuit breaker pattern
   - Enhance error handling and recovery

4. **Phase 4: Pipeline Optimization**
   - Improve parallel processing efficiency
   - Add batching support
   - Optimize resource usage

5. **Phase 5: Integration Testing**
   - Test with multiple LLMs
   - Verify pattern application
   - Ensure error recovery works properly

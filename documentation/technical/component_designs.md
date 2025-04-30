# Ultra Component Designs

This document describes the design of key components in the Ultra MVP.

## Frontend Components

### LLMSelector Component

The LLM Selector allows users to select which AI models to use for their analysis.

#### Props

| Prop | Type | Description |
|------|------|-------------|
| availableModels | string[] | List of available model IDs |
| selectedModels | string[] | Currently selected model IDs |
| primaryModel | string | Primary model for analysis |
| onSelectModels | function | Callback when selection changes |
| onSelectPrimary | function | Callback when primary model changes |
| isLoading | boolean | Loading state |

#### Component Structure

```tsx
<div className="llm-selector">
  <h3>Select AI Models</h3>
  <div className="models-grid">
    {availableModels.map(model => (
      <ModelCard
        key={model}
        model={model}
        isSelected={selectedModels.includes(model)}
        isPrimary={primaryModel === model}
        onSelect={() => onSelectModels(model)}
        onSetPrimary={() => onSelectPrimary(model)}
      />
    ))}
  </div>
  <div className="selection-summary">
    <p>Selected: {selectedModels.join(', ')}</p>
    <p>Primary: {primaryModel}</p>
  </div>
</div>
```

#### Behavior

- Users can select multiple models by clicking on model cards
- The primary model is marked with a special indicator
- At least one model must be selected at all times
- If the primary model is deselected, another model becomes primary

### AnalysisResults Component

Displays the results of an analysis from multiple LLMs.

#### Props

| Prop | Type | Description |
|------|------|-------------|
| results | AnalysisResult | Results of the analysis |
| isLoading | boolean | Loading state |
| error | string | Error message if any |
| viewMode | 'side-by-side' \| 'combined' | Display mode |
| onCopy | function | Copy text callback |
| onRerun | function | Re-run analysis callback |

#### Component Structure

```tsx
<div className="analysis-results">
  {isLoading ? (
    <LoadingSpinner message="Analyzing..." />
  ) : error ? (
    <ErrorDisplay message={error} onRetry={onRerun} />
  ) : (
    <>
      <div className="view-controls">
        <button onClick={() => setViewMode('side-by-side')}>Side by Side</button>
        <button onClick={() => setViewMode('combined')}>Combined View</button>
      </div>

      {viewMode === 'side-by-side' ? (
        <div className="models-grid">
          {Object.entries(results.modelResponses).map(([model, response]) => (
            <ModelResponseCard
              key={model}
              model={model}
              response={response}
              isPrimary={model === results.primaryModel}
              onCopy={() => onCopy(response)}
            />
          ))}
        </div>
      ) : (
        <div className="combined-analysis">
          <h3>Ultra Analysis</h3>
          <div className="combined-content">
            {results.ultraResponse}
          </div>
          <div className="action-buttons">
            <button onClick={() => onCopy(results.ultraResponse)}>Copy</button>
            <button onClick={onRerun}>Re-run Analysis</button>
          </div>
        </div>
      )}

      <PerformanceMetrics metrics={results.performance} />
    </>
  )}
</div>
```

#### Behavior

- Displays loading state during analysis
- Shows error message if analysis fails
- Offers side-by-side view of individual model responses
- Provides combined analysis view
- Includes performance metrics (time, tokens)
- Allows copying responses and re-running analysis

### PatternSelector Component

Allows users to select an analysis pattern for the LLM comparison.

#### Props

| Prop | Type | Description |
|------|------|-------------|
| patterns | AnalysisPattern[] | Available analysis patterns |
| selectedPattern | string | Current selected pattern ID |
| onSelect | function | Callback when pattern changes |

#### Component Structure

```tsx
<div className="pattern-selector">
  <h3>Select Analysis Pattern</h3>
  <div className="patterns-list">
    {patterns.map(pattern => (
      <div
        key={pattern.id}
        className={`pattern-item ${selectedPattern === pattern.id ? 'selected' : ''}`}
        onClick={() => onSelect(pattern.id)}
      >
        <h4>{pattern.name}</h4>
        <p>{pattern.description}</p>
      </div>
    ))}
  </div>
</div>
```

#### Behavior

- Displays a list of available analysis patterns
- Shows description for each pattern
- Highlights currently selected pattern
- Triggers callback when a pattern is selected

## Backend Components

### LLMService

The LLM Service manages connections to different LLM providers and handles the orchestration of requests.

#### Methods

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| analyze_prompt | Analyze a prompt with multiple LLMs | prompt, models, pattern | AnalysisResult |
| get_available_models | Get list of available models | none | string[] |
| execute_pattern | Run a specific analysis pattern | prompt, responses, pattern | string |

#### Implementation Details

```python
class LLMService:
    def __init__(self, config):
        self.config = config
        self.clients = {}
        self.pattern_handlers = {
            "gut": self._execute_gut_check,
            "confidence": self._execute_confidence_analysis,
            "critique": self._execute_critique_analysis,
            # Other pattern handlers
        }

    async def initialize(self):
        # Initialize LLM clients based on configuration
        if self.config.enable_openai:
            self.clients["openai"] = OpenAIClient(
                api_key=self.config.openai_api_key,
                org_id=self.config.openai_org_id
            )

        # Initialize other clients similarly

    async def get_available_models(self):
        # Collect and return all available models from all clients
        models = []
        for client_name, client in self.clients.items():
            try:
                client_models = await client.get_available_models()
                models.extend(client_models)
            except Exception as e:
                logger.error(f"Failed to get models from {client_name}: {e}")

        return models

    async def analyze_prompt(self, prompt, models, ultra_model, pattern):
        # Validate inputs
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        if not models:
            raise ValueError("At least one model must be selected")

        # Start performance tracking
        start_time = time.time()

        # Make concurrent requests to all selected models
        responses = {}
        tasks = []

        for model in models:
            client = self._get_client_for_model(model)
            if client:
                task = asyncio.create_task(
                    client.generate_response(prompt, model=model)
                )
                tasks.append((model, task))

        # Wait for all responses
        for model, task in tasks:
            try:
                response = await task
                responses[model] = response
            except Exception as e:
                logger.error(f"Failed to get response from {model}: {e}")
                responses[model] = {"error": str(e)}

        # Execute the selected pattern
        ultra_response = await self.execute_pattern(
            prompt=prompt,
            responses=responses,
            pattern=pattern,
            ultra_model=ultra_model
        )

        # Calculate performance metrics
        end_time = time.time()
        performance = {
            "total_time_seconds": end_time - start_time,
            "model_times": {model: resp.get("time_taken", 0) for model, resp in responses.items()},
            "token_counts": {model: resp.get("token_count", {}) for model, resp in responses.items()}
        }

        # Return combined result
        return {
            "model_responses": {model: resp.get("text", "") for model, resp in responses.items()},
            "ultra_response": ultra_response,
            "performance": performance,
            "pattern": pattern
        }

    async def execute_pattern(self, prompt, responses, pattern, ultra_model):
        """Execute a specific analysis pattern"""
        handler = self.pattern_handlers.get(pattern)
        if not handler:
            raise ValueError(f"Unknown pattern: {pattern}")

        return await handler(prompt, responses, ultra_model)

    # Private pattern execution methods
    async def _execute_gut_check(self, prompt, responses, ultra_model):
        # Implementation of gut check pattern
        pass

    async def _execute_confidence_analysis(self, prompt, responses, ultra_model):
        # Implementation of confidence analysis pattern
        pass

    # Other private methods
    def _get_client_for_model(self, model):
        # Map model to appropriate client
        pass
```

### API Endpoints

The API layer exposes the LLM functionality through RESTful endpoints.

#### Key Endpoints

##### POST /api/analyze

Analyzes a prompt using multiple LLMs.

**Request:**

```json
{
  "prompt": "What are the pros and cons of renewable energy?",
  "models": ["gpt4o", "claude37", "gemini15"],
  "ultra_model": "gpt4o",
  "pattern": "confidence",
  "options": {}
}
```

**Response:**

```json
{
  "status": "success",
  "model_responses": {
    "gpt4o": "GPT-4o's detailed response...",
    "claude37": "Claude's detailed response...",
    "gemini15": "Gemini's detailed response..."
  },
  "ultra_response": "The combined analysis based on all models...",
  "performance": {
    "total_time_seconds": 3.45,
    "model_times": {
      "gpt4o": 2.1,
      "claude37": 3.2,
      "gemini15": 1.8
    },
    "token_counts": {
      "gpt4o": {
        "prompt_tokens": 15,
        "completion_tokens": 230,
        "total_tokens": 245
      },
      "claude37": {
        "prompt_tokens": 15,
        "completion_tokens": 280,
        "total_tokens": 295
      },
      "gemini15": {
        "prompt_tokens": 15,
        "completion_tokens": 190,
        "total_tokens": 205
      }
    }
  }
}
```

##### GET /api/available-models

Returns a list of available models.

**Response:**

```json
{
  "status": "success",
  "available_models": [
    "gpt4o",
    "gpt4turbo",
    "claude37",
    "claude3opus",
    "gemini15",
    "llama3"
  ],
  "errors": {}
}
```

## Analysis Patterns

### Pattern Implementation

Analysis patterns are implemented as specialized handlers that process multiple LLM responses.

#### Base Pattern Structure

```python
class AnalysisPattern:
    def __init__(self, config=None):
        self.config = config or {}

    async def execute(self, prompt, responses, ultra_model):
        """Execute the pattern analysis"""
        raise NotImplementedError("Subclasses must implement this method")

    def _extract_text_from_responses(self, responses):
        """Helper to extract text from response objects"""
        return {model: resp.get("text", "") for model, resp in responses.items()}
```

#### Confidence Analysis Pattern

```python
class ConfidenceAnalysisPattern(AnalysisPattern):
    async def execute(self, prompt, responses, ultra_model):
        # Extract text responses
        model_texts = self._extract_text_from_responses(responses)

        # Ask the ultra model to analyze confidence levels
        analysis_prompt = f"""
        Original prompt: {prompt}

        Here are responses from different models:

        {self._format_responses(model_texts)}

        Analyze these responses and determine which has the highest confidence.
        Evaluate factual accuracy, reasoning quality, and certainty.
        Provide a confidence score (0-100%) for each response and explain your reasoning.
        Then provide a final conclusion about which response is most likely correct and why.
        """

        # Get the confidence analysis from the ultra model
        ultra_client = self._get_client_for_model(ultra_model)
        analysis_result = await ultra_client.generate_response(analysis_prompt)

        return analysis_result.get("text", "Analysis failed")

    def _format_responses(self, model_texts):
        """Format the model responses for the analysis prompt"""
        formatted = ""
        for model, text in model_texts.items():
            formatted += f"--- {model} Response ---\n{text}\n\n"
        return formatted
```

## Cache Implementation

The caching system improves performance by storing and retrieving results for identical requests.

### CacheService

```python
class CacheService:
    def __init__(self, config):
        self.config = config
        self.cache = {}
        self.max_size = config.max_cache_items
        self.ttl = config.cache_ttl

    def get(self, key):
        """Get a cached item if it exists and is not expired"""
        if key not in self.cache:
            return None

        cached_item = self.cache[key]
        if time.time() > cached_item["expires_at"]:
            del self.cache[key]
            return None

        return cached_item["value"]

    def set(self, key, value):
        """Add an item to the cache"""
        # Evict items if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + self.ttl
        }

    def _evict_oldest(self):
        """Evict the oldest item from the cache"""
        if not self.cache:
            return

        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k]["created_at"]
        )
        del self.cache[oldest_key]

    def generate_key(self, prompt, models, pattern, options=None):
        """Generate a cache key from request parameters"""
        key_parts = [
            prompt,
            ",".join(sorted(models)),
            pattern,
            json.dumps(options or {}, sort_keys=True)
        ]
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()
```

# MVP Technical Design

## System Architecture Overview

The Ultra MVP consists of three primary components:

1. **Frontend UI**: React-based UI for selecting models, entering prompts, and viewing comparison results
2. **Backend API**: FastAPI-based service for handling requests and orchestrating LLM calls
3. **LLM Integrations**: Client libraries for connecting to various LLM providers

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  Frontend   │     │   Backend    │     │  LLM Service  │
│    React    │────▶│   FastAPI    │────▶│  Orchestrator │
└─────────────┘     └──────────────┘     └───────────────┘
                                                 │
                                                 ▼
                  ┌──────────────────────────────────────────┐
                  │                                          │
          ┌───────┴──────┐    ┌───────────────┐    ┌────────┴─────┐
          │   OpenAI     │    │   Anthropic   │    │    Google    │
          │   (GPT-4)    │    │   (Claude)    │    │   (Gemini)   │
          └──────────────┘    └───────────────┘    └──────────────┘
```

## Key Components

### 1. Frontend UI

- **LLMSelector Component**: Allows users to select which models to include in analysis
- **PromptInput Component**: Text area for entering prompts
- **AnalysisResults Component**: Displays response from each model and the Ultra synthesis
- **ComparisonView Component**: Side-by-side comparison of model outputs

### 2. Backend API

- **/api/llms Endpoint**: Returns available LLM models and their status
- **/api/analyze Endpoint**: Core endpoint for initiating model comparison
- **/api/patterns Endpoint**: Returns available analysis patterns

### 3. LLM Orchestration

- **MultiLLMOrchestrator Class**: Manages distribution of requests to multiple LLMs
- **ModelResponse Class**: Standardized format for LLM responses
- **Caching Layer**: Redis-based caching for reducing duplicate API calls

## Integration Flow

1. User selects models and inputs prompt in frontend
2. Frontend sends request to `/api/analyze` endpoint
3. Backend validates request and passes to orchestrator
4. Orchestrator:
   - Distributes request to selected models in parallel
   - Collects and standardizes responses
   - Generates a synthesis if requested
   - Returns all results to the frontend
5. Frontend displays results in comparison view

## Critical Components for MVP

### API Endpoint Implementation

The `/api/analyze` endpoint is critical and must:

- Accept a prompt and list of selected models
- Handle request validation
- Pass request to orchestrator
- Implement proper error handling
- Return standardized response format

```python
@app.post("/api/analyze")
async def analyze_prompt(request: AnalysisRequest):
    """
    Analyze a prompt using multiple LLMs and an Ultra LLM
    """
    try:
        # Validate request
        if not request.prompt:
            raise ValueError("Prompt cannot be empty")
        if not request.selected_models:
            raise ValueError("At least one model must be selected")

        # Orchestrate LLM responses
        results = await orchestrator.process_responses(
            prompt=request.prompt,
            models=request.selected_models,
            ultra_model=request.ultra_model
        )

        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

### Orchestrator Implementation

The orchestrator must efficiently manage multiple LLM requests:

```python
async def process_responses(self, prompt, models, ultra_model=None):
    """Process prompt with multiple models"""
    # Get responses from selected models in parallel
    tasks = [self.get_model_response(model, prompt) for model in models]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out errors
    valid_responses = {
        model: resp for model, resp in zip(models, responses)
        if not isinstance(resp, Exception)
    }

    # Generate ultra synthesis if requested
    synthesis = None
    if ultra_model and valid_responses:
        synthesis = await self.get_synthesis(valid_responses, prompt, ultra_model)

    return {
        "model_responses": valid_responses,
        "ultra_response": synthesis
    }
```

### Frontend Integration

The frontend must properly connect to the backend and display results:

```javascript
const analyzePrompt = async (prompt, selectedModels, ultraModel) => {
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        selected_models: selectedModels,
        ultra_model: ultraModel
      })
    });

    const data = await response.json();

    if (data.status === 'error') {
      throw new Error(data.message);
    }

    return data.results;
  } catch (error) {
    console.error('Analysis failed:', error);
    throw error;
  }
};
```

## Environment Configuration

The MVP requires environment configuration for LLM API keys:

```
# .env.example
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
OLLAMA_BASE_URL=http://localhost:11434
```

## Error Handling Strategy

The MVP must implement proper error handling at multiple levels:

1. **Frontend**: Display user-friendly error messages and retry options
2. **Backend API**: Return standardized error responses with clear messages
3. **LLM Clients**: Implement retries and fallbacks for API failures
4. **Orchestrator**: Handle partial failures (when some models fail, others succeed)

## Testing Strategy

The MVP requires testing at multiple levels:

1. **Unit Tests**: For individual components (orchestrator, API endpoints)
2. **Integration Tests**: For the full request flow
3. **Mock LLM Tests**: Using mock responses for reliable testing
4. **End-to-End Tests**: With actual LLM services

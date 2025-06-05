# Minimal Orchestrator Design

## Goal
Build the simplest possible working orchestrator that proves the core UltraAI value: multiple models working together produce better results than one model alone.

## Phase 1: Absolute Minimum (v0.1)

### Single Endpoint
```
POST /api/orchestrate/simple
{
    "prompt": "What is the meaning of life?",
    "models": ["gpt-4", "claude-3"]  // Optional, defaults to ["gpt-4", "claude-3"]
}
```

### Response
```json
{
    "responses": [
        {
            "model": "gpt-4",
            "response": "...",
            "time": 2.3
        },
        {
            "model": "claude-3",
            "response": "...",
            "time": 1.8
        }
    ],
    "synthesis": "Based on both models: ...",  // Simple GPT-4 summary
    "total_time": 3.1
}
```

### Implementation Plan

1. **File: `backend/services/minimal_orchestrator.py`**
   - Simple class with async methods
   - Parallel API calls using asyncio.gather()
   - 30-second timeout per model
   - Basic error handling

2. **File: `backend/routes/orchestrator_minimal.py`**
   - Single POST endpoint
   - Input validation
   - Call orchestrator service
   - Return formatted response

3. **Supported Models (Already have API keys)**
   - OpenAI: gpt-4, gpt-3.5-turbo
   - Anthropic: claude-3-opus, claude-3-sonnet
   - Google: gemini-pro

## Code Structure

```python
# minimal_orchestrator.py
class MinimalOrchestrator:
    def __init__(self):
        self.clients = self._init_clients()
    
    async def orchestrate(self, prompt: str, models: List[str]):
        # 1. Create tasks for each model
        # 2. Run in parallel with asyncio.gather()
        # 3. Synthesize with GPT-4
        # 4. Return results

# orchestrator_minimal.py (routes)
@router.post("/api/orchestrate/simple")
async def simple_orchestrate(request: SimpleRequest):
    # Validate input
    # Call orchestrator
    # Return response
```

## Success Metrics
- Response time < 10 seconds
- All 3 LLM providers work
- Clean error handling
- Simple synthesis shows value

## What We're NOT Doing (Yet)
- No complex patterns
- No multi-stage analysis
- No caching
- No document support
- No fancy UI
- No user preferences

## Next Phases (One per week)
- Week 2: Add "compare" mode (highlight differences)
- Week 3: Add "consensus" mode (find agreements)
- Week 4: Add "critique" mode (models review each other)
- Week 5: Add document context support

## Testing Plan
1. Test each LLM individually
2. Test parallel execution
3. Test timeout handling
4. Test synthesis
5. Deploy and verify on Render
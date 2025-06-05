# Orchestrator Integration Audit

## Current State Analysis

After removing the orchestrator, here's what's left dangling:

### 1. Frontend Integration Points

**Frontend expects:**
- Endpoint: `/api/orchestrator/feather` (from api.ts line 171)
- Request format:
  ```json
  {
    "prompt": "...",
    "models": ["gpt-4", "claude-3"],
    "args": {
      "pattern": "gut",
      "ultra_model": "gpt-4",
      "output_format": "txt"
    },
    "kwargs": {}
  }
  ```
- Response format: AnalysisResponse with model_responses, ultra_response, performance metrics

### 2. Backend Routes That Reference Orchestration

**Files that import/reference orchestrator:**
- `backend/routes/document_analysis_routes.py` - "integrating with the Ultra LLM orchestrator"
- `backend/routes/analyze_routes.py` - analysis endpoints
- `backend/app.py` - Line 41: "# Orchestrator routes removed for rebuild"

**Available routes that might be used:**
- `/api/analyze` - from analyze_routes.py
- `/api/document-analysis` - from document_analysis_routes.py
- `/api/available-models` - from available_models_routes.py

### 3. Services That Support Orchestration

**Existing services that orchestrator would use:**
- `llm_config_service.py` - LLM configuration management
- `prompt_service.py` - Prompt templating
- `cache_service.py` - Response caching
- `document_processor.py` - Document handling
- `analysis_service.py` - Analysis logic

### 4. Missing Core Component

**What's completely missing:**
- The actual orchestrator service that:
  - Takes requests from frontend
  - Calls multiple LLMs in parallel
  - Synthesizes responses
  - Returns unified result

## Integration Strategy

### Option 1: Minimal Drop-in Replacement

Create a simple orchestrator that:
1. Exposes `/api/orchestrator/feather` endpoint
2. Accepts the existing request format
3. Calls LLMs using existing services
4. Returns expected response format

### Option 2: Redirect to Existing Routes

Use existing analyze_routes.py and:
1. Add a compatibility endpoint at `/api/orchestrator/feather`
2. Transform request to match analyze_routes format
3. Use existing analysis logic

### Option 3: Complete New Implementation

Build fresh orchestrator that:
1. Creates new endpoint `/api/orchestrate/simple`
2. Updates frontend to use new endpoint
3. Simplified request/response format

## Recommended Approach

**Go with Option 1** - Minimal Drop-in Replacement because:
- Frontend already expects specific endpoint and format
- No frontend changes needed
- Can reuse existing services
- Fastest path to working system
- Can evolve later

## Implementation Checklist

1. **Create minimal orchestrator service:**
   - `backend/services/minimal_orchestrator.py`
   - Reuse `llm_config_service` for LLM connections
   - Simple parallel execution with asyncio

2. **Add orchestrator route:**
   - `backend/routes/orchestrator_minimal.py`
   - Mount at `/api/orchestrator/feather` for compatibility
   - Transform request/response as needed

3. **Wire into app.py:**
   - Import new route
   - Register with FastAPI app

4. **Test with existing frontend:**
   - No frontend changes needed
   - Should "just work"

## Dependencies to Verify

1. **API Keys:** Already configured in environment
   - OPENAI_API_KEY
   - ANTHROPIC_API_KEY
   - GOOGLE_API_KEY

2. **LLM Services:** Check if they exist or need creation
   - OpenAI client
   - Anthropic client
   - Google Gemini client

3. **Model Mappings:** Frontend uses these model names
   - gpt4o → OpenAI GPT-4
   - claude37 → Anthropic Claude 3
   - gemini15 → Google Gemini Pro

## Next Steps

1. Update PLAN to include this integration strategy
2. Write tests for the drop-in orchestrator
3. Implement minimal orchestrator matching existing API contract
4. Test with frontend without any frontend changes
5. Deploy and verify
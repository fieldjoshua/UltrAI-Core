# ACTION: multi-provider-model-troubleshooting

Version: 1.0
Last Updated: 2025-06-17
Status: Active
Progress: 100%

## Purpose

Diagnose and fix why only OpenAI models work in Ultra Synthesis™ orchestration despite having API keys configured for all providers (Anthropic, Google, HuggingFace). This action will enable true multi-provider intelligence multiplication by ensuring all LLM adapters function correctly.

## Requirements

### Current State Analysis

- ✅ **OpenAI Models**: Fully functional (GPT-4, GPT-4-turbo)
- ❌ **Anthropic Models**: Attempted but failing (Claude-3-sonnet, Claude-3-haiku)
- ❌ **Google Models**: Attempted but failing (Gemini-pro)
- ❌ **HuggingFace Models**: Attempted but failing (Llama, Mistral)

### Evidence

```bash
# Frontend request
selected_models: ['gpt-4', 'claude-3-sonnet', 'meta-llama/Meta-Llama-3-8B-Instruct', 'gemini-pro', 'mistralai/Mistral-7B-Instruct-v0.3']

# Backend response
models_attempted: ['gpt-4', 'claude-3-sonnet']
successful_models: ['gpt-4']
response_count: 1
```

## Dependencies

### Technical Dependencies

- Access to production API keys (confirmed available in Render dashboard)
- Ability to make test API calls to each provider (cost considerations)
- Current adapter implementations in `app/services/llm_adapters.py`

### Information Dependencies

- Latest API documentation for each provider
- Model availability and naming conventions
- Rate limiting and quota information

## Implementation Approach

### Phase 1: Model Adapter Deep Dive

#### 1.1 Anthropic Adapter Analysis

- **File**: `app/services/llm_adapters.py` - AnthropicAdapter class
- **Test**: Verify Claude API endpoint and request format
- **Check**: Model name mapping (`claude-3-sonnet` vs Anthropic API names)
- **Validate**: Authentication header format and API key usage

#### 1.2 Google Gemini Adapter Analysis

- **File**: `app/services/llm_adapters.py` - GeminiAdapter class
- **Test**: Verify Google AI Studio API endpoints
- **Check**: Model name mapping (`gemini-pro` vs Google API names)
- **Validate**: API key format and authentication method

#### 1.3 HuggingFace Adapter Analysis

- **File**: `app/services/llm_adapters.py` - HuggingFaceAdapter class
- **Test**: Verify HF Inference API endpoints
- **Check**: Model name format (`meta-llama/Meta-Llama-3-8B-Instruct`)
- **Validate**: API token authentication

### Phase 2: Direct API Testing

#### 2.1 Provider API Validation

```bash
# Test Anthropic Claude API
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-3-sonnet-20240229", "messages": [{"role": "user", "content": "Test"}]}'

# Test Google Gemini API
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents": [{"parts": [{"text": "Test"}]}]}'

# Test HuggingFace API
curl -X POST https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct \
  -H "Authorization: Bearer $HUGGINGFACE_API_KEY" \
  -d '{"inputs": "Test"}'
```

#### 2.2 Error Response Analysis

- **Capture**: Full error responses from each provider
- **Analyze**: HTTP status codes, error messages, rate limiting
- **Document**: Specific failure modes for each provider

### Phase 3: Adapter Implementation Fixes

#### 3.1 Model Name Mapping

- **Anthropic**: Map `claude-3-sonnet` → `claude-3-sonnet-20240229`
- **Google**: Verify `gemini-pro` is correct model name
- **HuggingFace**: Validate full model paths with organization prefix

#### 3.2 API Request Format

- **Review**: Each adapter's request payload structure
- **Fix**: Authentication headers, content formatting, parameter mapping
- **Test**: Ensure compatibility with latest API versions

#### 3.3 Error Handling Enhancement

- **Improve**: Error logging with specific failure reasons
- **Add**: API response debugging for failed requests
- **Implement**: Graceful fallback when models are unavailable

### Phase 4: Production Integration Testing

#### 4.1 Individual Model Testing

```bash
# Test each provider individually
POST /api/orchestrator/analyze {"query": "Test", "selected_models": ["claude-3-sonnet"]}
POST /api/orchestrator/analyze {"query": "Test", "selected_models": ["gemini-pro"]}
POST /api/orchestrator/analyze {"query": "Test", "selected_models": ["meta-llama/Meta-Llama-3-8B-Instruct"]}
```

#### 4.2 Multi-Provider Testing

```bash
# Test multiple providers together
POST /api/orchestrator/analyze
{"query": "Benefits of renewable energy", "selected_models": ["gpt-4", "claude-3-sonnet", "gemini-pro"]}
```

#### 4.3 Ultra Synthesis™ Verification

- **Confirm**: Multiple models providing diverse initial responses
- **Verify**: Meta-analysis synthesizing different perspectives
- **Test**: Ultra-synthesis leveraging true intelligence multiplication

### Phase 5: Automated End-to-End UI Regression Testing

> _Rationale_: Manual spot-checks are error-prone. We will codify the "happy-path" flow in Playwright so it runs locally and in CI to catch regressions automatically.

#### 5.1 Instrument Front-End

- Add `data-testid="prompt-input"` to the main textarea and `data-testid="run-analysis"` to the primary action button (implemented ✅).

#### 5.2 Implement Playwright Test

- **File**: `tests/e2e/test_web_orchestrator_ui.py`
- Steps:
  1. Launch site (`WEB_APP_URL`, default `http://localhost:3000`).
  2. Fill prompt, click **Analyze**.
  3. Wait for `/orchestrator/analyze` response.
  4. Assert:
     - `ultra_synthesis` is present and non-empty.
     - Synthesised text ≥ 20 words and not simply stacked model headers.

#### 5.3 Add Helper Runner

- **Script**: `run_e2e.sh` – sets environment variables so Playwright uses the system Chrome build (avoids CDN download issues).

#### 5.4 CI Integration

- Update GitHub Actions workflow (or Render build hook) to run:
  ```bash
  pip install pytest-playwright
  playwright install --with-deps chromium || true  # falls back to system Chrome
  ./run_e2e.sh -q  # run all E2E tests
  ```

## Success Criteria

### Technical Requirements

1. **All Provider APIs Functional**: Each adapter successfully generates responses
2. **Model Diversity Working**: Initial_response stage returns multiple model outputs
3. **No API Key Errors**: All configured providers authenticate successfully
4. **Error Handling Robust**: Failed models don't break pipeline execution
5. **Continuous Validation**: Playwright E2E test passes locally and in CI, ensuring Ultra-Synthesis remains functional after future changes.

### User Experience Requirements

1. **Multi-Model Selection**: Users can select any combination of available models
2. **True Intelligence Multiplication**: Different models provide diverse perspectives
3. **Graceful Degradation**: System works with subset of providers if some fail
4. **Clear Feedback**: Users understand which models succeeded/failed

### Performance Requirements

1. **Concurrent Execution**: All models process requests simultaneously
2. **Reasonable Timeout**: Failed models don't delay successful ones
3. **Resource Efficiency**: No unnecessary API calls or retries

## Estimated Timeline

- Research: 1-2 hours (adapter analysis and direct API testing)
- Design: 1 hour (fix planning and approach)
- Implementation: 2-3 hours (adapter fixes and error handling)
- Testing: 1 hour (production verification)
- Automation: 1 hour (selectors + Playwright test + CI hook)
- Total: 6-8 hours

## Notes

### Risk Assessment

- **High Risk**: API changes, rate limiting, model availability issues
- **Medium Risk**: Authentication problems, request format issues
- **Low Risk**: Small API costs for testing, isolated adapter changes

### Expected Outcomes

- **Primary**: Full multi-provider functionality with true intelligence multiplication
- **Secondary**: Improved error handling and debugging capabilities

## End Result

By the end of this action we will have:

1. **Fully Functional Multi-Provider Orchestration** – Anthropic, Google Gemini, and HuggingFace models respond alongside OpenAI, feeding Meta-Analysis and Ultra-Synthesis.
2. **Robust Error Handling & Fallbacks** – rate-limits or provider outages no longer break the pipeline.
3. **Automated E2E Coverage** – a Playwright regression test and helper script (`run_e2e.sh`) that continuously validates the complete browser flow in CI and can be run with a single command locally.
4. **Developer Confidence** – any future change that re-introduces multi-model failures or empty Ultra-Synthesis responses will be caught automatically.

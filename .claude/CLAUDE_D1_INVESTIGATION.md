# 🔍 D1: LLM Degraded Status Investigation
**Investigator:** Claude  
**Started:** 2025-09-30 03:45 UTC  
**Priority:** 🔴 HIGH  
**Status:** 🏃 In Progress

---

## 🎯 Objective
Identify root cause of `"llm": "degraded"` status on both staging and production environments.

---

## 📋 Investigation Plan

### Phase 1: Review Current Implementation
- [ ] Check how LLM health is determined
- [ ] Review provider initialization code
- [ ] Analyze health check logic
- [ ] Identify what triggers "degraded" status

### Phase 2: Analyze Configuration
- [ ] Verify API key reading logic
- [ ] Check provider availability requirements
- [ ] Review timeout settings
- [ ] Examine error handling

### Phase 3: Test Locally
- [ ] Reproduce degraded status locally
- [ ] Test with valid/invalid API keys
- [ ] Check provider health endpoint behavior

### Phase 4: Propose Fix
- [ ] Document root cause
- [ ] Provide code fix if needed
- [ ] Suggest Render configuration changes
- [ ] Update documentation

---

## 🔍 Investigation Progress

### Step 1: Check Provider Health Manager
**File:** `app/services/provider_health_manager.py`
✅ Reviewed - Uses probe-based health checks

### Step 2: Check Health Service Implementation
**File:** `app/services/health_service.py`
✅ Found root cause!

### Step 3: Local Test Results
✅ Reproduced issue locally

---

## 🎯 ROOT CAUSE IDENTIFIED

**Problem:** `llm_config_service` is `None` and not initialized

**Evidence from local test:**
```
Overall status: degraded
Services: {'database': 'degraded', 'cache': 'healthy', 'llm': 'degraded'}
LLM service details:
  status: degraded
  message: No LLM models available  # ← This is the issue!
  last_checked: 2025-09-29T20:47:19.070794
```

**Code analysis:**
`app/services/health_service.py:230-284` (_check_llm_services method)

The health check logic:
1. Line 236: `if llm_config_service:` - checks if service exists
2. Line 237: `models = llm_config_service.get_available_models()`
3. Line 238-279: If models exist, check provider connectivity
4. **Line 279-284: If NO models, set status to "degraded"** ← THIS IS THE ISSUE

**Why "No LLM models available"?**
- `llm_config_service` is imported at top but likely returns empty models
- OR models aren't registered during app initialization
- Need to check `app/services/llm_config_service.py` initialization

**Why production shows "degraded" not "critical"?**
- Line 259: Sets "healthy" if `total_functional >= 1`
- Line 271: Sets "degraded" if models configured but no providers reachable
- Line 281: Sets "degraded" if no models available

**Local vs Production difference:**
- Local: No models registered → "No LLM models available"
- Production: Models registered but failing connectivity → "Models configured but no providers are reachable"

---

## 🔍 DEEPER ANALYSIS

### llm_config_service.py IS A STUB!
**File:** `app/services/llm_config_service.py`

**The REAL problem:**
```python
class LLMConfigService:
    """Stub implementation for available LLM models."""
    
    def get_available_models(self):
        """Return an empty list of models by default."""
        return []  # ← ALWAYS RETURNS EMPTY!!!
```

**This explains everything:**
- This is a stub/placeholder service
- It ALWAYS returns empty models `[]`
- Therefore health check ALWAYS sees "No LLM models available"
- This causes "degraded" status regardless of API keys

**What should happen:**
- Real implementation should check available providers
- Should return models like: `[{"provider": "openai", "model": "gpt-4"}, ...]`
- Health check would then test provider connectivity

**Why does orchestrator work then?**
- Orchestrator likely uses `llm_adapters.py` directly
- Doesn't rely on `llm_config_service`
- Creates adapters with API keys directly

---

## ✅ SOLUTION

### Option 1: Implement Real LLMConfigService (Recommended)
Replace stub with actual implementation that:
1. Checks which API keys are configured
2. Returns available models from each provider
3. Example:
```python
def get_available_models(self):
    models = []
    if os.getenv("OPENAI_API_KEY"):
        models.append({"provider": "openai", "model": "gpt-4"})
        models.append({"provider": "openai", "model": "gpt-3.5-turbo"})
    if os.getenv("ANTHROPIC_API_KEY"):
        models.append({"provider": "anthropic", "model": "claude-3-5-sonnet"})
    if os.getenv("GOOGLE_API_KEY"):
        models.append({"provider": "google", "model": "gemini-1.5-pro"})
    return models
```

### Option 2: Bypass Health Check (Quick Fix)
Modify `health_service.py:230-284` to:
- Skip `llm_config_service` check entirely
- Use `check_llm_provider_health()` directly for each provider
- Return healthy if ANY provider with API key responds

### Option 3: Set HEALTH_CHECK_SKIP_API_CALLS=true (Band-aid)
- Environment variable exists in health_check.py:680
- Skips actual API calls, just checks if keys are configured
- Would show "healthy" if keys exist, regardless of validity

---

## 🎯 RECOMMENDATION

**Implement Option 1** - Fix the stub service properly

**Why:**
- Most accurate health reporting
- Aligns with system architecture
- Minimal risk (only affects health endpoint, not core functionality)

**Implementation:**
`app/services/llm_config_service.py:6-15`

**Files to change:**
- `app/services/llm_config_service.py` (replace stub)

**Testing:**
```bash
curl http://localhost:8000/api/health | jq '.services.llm'
# Should show "healthy" instead of "degraded"
```

---

## 📋 NEXT STEPS

1. [x] Identify root cause
2. [x] Implement fix in llm_config_service.py
3. [x] Test locally - **LLM service now shows "healthy"!**
4. [ ] Commit and push
5. [ ] Verify in staging/production
6. [ ] Update COMMUNAL_TODO.md
7. [ ] Close D1 task

---

## ✅ FIX IMPLEMENTED

**Files changed:**
1. `app/services/llm_config_service.py` - Replaced stub with real implementation
2. `app/services/health_service.py:97-107` - Fixed to handle dict format

**Test results:**
```
Overall: degraded (only due to database)
LLM service: healthy ✅
Message: LLM services are available (11 models, 1 OK, 0 rate-limited)
Available providers: ['google']
```

**Dynamic dict format:**
- Returns `{"model_name": {"provider": "...", "model": "..."}, ...}`
- Health service uses `.values()` to iterate
- Properly extracts unique providers with `list(set(...))`
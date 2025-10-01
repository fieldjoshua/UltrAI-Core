# Output Error States Catalog

This document catalogs all error and degraded states in the UltrAI orchestration system, mapping backend status strings to frontend display locations.

## Backend Status Strings

### GET /orchestrator/status

Returns `StatusResponse` with `status` field containing one of three values:

#### 1. healthy

**Condition:**
- `model_count >= MINIMUM_MODELS_REQUIRED` (default: 3)
- `available_providers >= 2`

**Backend Response:**
```json
{
  "status": "healthy",
  "service_available": true,
  "message": "Service operational with {N} models"
}
```

**Location:** `app/routes/orchestrator_minimal.py:212-214`

---

#### 2. degraded

**Condition:**
- `model_count >= 1` AND
- `Config.ENABLE_SINGLE_MODEL_FALLBACK == True`

**Backend Response:**
```json
{
  "status": "degraded",
  "service_available": true,
  "message": "Service in degraded mode with only {N} model(s)"
}
```

**Location:** `app/routes/orchestrator_minimal.py:216-218`

**Alternative Message (with provider health):**
```
degradation_message = await provider_health_manager.get_degradation_message()
```

**Example:** `"Service degraded: Only 2 of 3 required providers available"`

---

#### 3. unavailable

**Condition:**
- `model_count < MINIMUM_MODELS_REQUIRED` OR
- Missing required providers

**Backend Response:**
```json
{
  "status": "unavailable",
  "service_available": false,
  "message": "Service unavailable. Only {N} model(s) available, {M} required"
}
```

**Location:** `app/routes/orchestrator_minimal.py:220-222`

---

## Frontend Display Locations

### 1. OrchestratorInterface.jsx

**Service Unavailable Banner**

**Condition:** `availableModels.length < 2`

**Location:** `frontend/src/components/OrchestratorInterface.jsx:366-399`

**Copy:**
```
Service Unavailable

UltraAI requires at least 2 different AI models for its multi-model 
orchestration system. Currently, only {N} model(s) are available.

Please ensure API keys are configured for at least 2 different AI providers.
```

**Visual:** Red warning banner with alert icon

---

**Button Disabled State**

**Condition:** `availableModels.length < 2`

**Location:** `frontend/src/components/OrchestratorInterface.jsx:561-562`

**Copy:** `"Need 2+ models to jam"`

---

**Degradation Toast**

**Condition:** `response.pipeline_info.service_status` is present

**Location:** `frontend/src/components/OrchestratorInterface.jsx:287-290`

**Copy:** Value from `pipeline_info.service_status` (e.g., "Service degraded: Only 2 of 3 required providers available")

**Visual:** Yellow warning toast (appears after analysis completes)

---

### 2. Wizard Components

**Initial Screen Model Availability Warning**

**Location:** Search for "insufficient models" or "API keys" in wizard files

**Expected Copy:** Similar to OrchestratorInterface banner

---

## HTTP Error Responses

### 503 Service Unavailable

**Condition:** Insufficient models or providers at request time

**Backend:**
```python
# orchestrator_minimal.py:334-340
raise HTTPException(
    status_code=503, 
    detail=f"UltraAI requires at least {required_models} models to proceed"
)
```

**Frontend Handling:**
```typescript
// orchestrator.ts:51-56
if (!response.ok) {
  const errorData = await response.json().catch(() => ({}));
  return {
    error: errorData.detail || `HTTP ${response.status}`,
    status: 'error',
  };
}
```

---

### 500 Internal Server Error

**Condition:** Unexpected pipeline failure

**Backend:**
```python
# orchestrator_minimal.py:719
raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
```

---

### Pipeline-Level Errors

**Condition:** Pipeline completes but with errors

**Response Shape:**
```json
{
  "success": false,
  "results": {
    "error": "Ultra Synthesis stage not completed",
    "status": "failed"
  },
  "error": "An unexpected error occurred: {message}"
}
```

---

## State Mapping Table

| Backend Status | service_available | Frontend Display | User Action |
|----------------|-------------------|------------------|-------------|
| `healthy` | `true` | Normal operation, all features enabled | None |
| `degraded` | `true` | Yellow toast with degradation message | Continue with caution |
| `unavailable` | `false` | Red banner, submit button disabled | Configure API keys |
| (HTTP 503) | N/A | Error response with detail message | Check service status |
| (HTTP 500) | N/A | Generic error message | Retry or contact support |

---

## Copy Guidelines

### Tone for Each State

1. **healthy**: Confident, invisible (no message needed)
2. **degraded**: Informative but reassuring ("Service still works, but...")
3. **unavailable**: Clear and actionable ("You need to do X")

### Recommended Copy Updates

**Current (unavailable):**
> "UltraAI requires at least 2 different AI models for its multi-model orchestration system."

**Suggested:**
> "UltrAI needs 2+ AI models to work its magic. Add API keys to get started."

**Current (degraded toast):**
> "Service degraded: Only 2 of 3 required providers available"

**Suggested:**
> "Running with 2 models (3 recommended). Answers may vary."

---

## Testing Error States

### Backend Tests

```bash
# Test insufficient models
MINIMUM_MODELS_REQUIRED=3 pytest tests/unit/test_orchestrator_status.py

# Test degraded mode
ENABLE_SINGLE_MODEL_FALLBACK=true pytest tests/integration/test_degraded_mode.py
```

### Frontend Tests

```bash
# Test unavailable banner rendering
npm test -- OrchestratorInterface.test.tsx --testNamePattern="unavailable"
```

---

## Related Files

**Backend:**
- `app/routes/orchestrator_minimal.py` (status endpoint + analyze endpoint)
- `app/services/provider_health_manager.py` (degradation messages)
- `app/config.py` (MINIMUM_MODELS_REQUIRED, ENABLE_SINGLE_MODEL_FALLBACK)

**Frontend:**
- `frontend/src/components/OrchestratorInterface.jsx` (lines 366-399, 561-562, 287-290)
- `frontend/src/api/orchestrator.ts` (error handling)
- `frontend/src/components/wizard/CyberWizard.tsx` (wizard error states)

---

## Future Improvements

1. **Standardize Error Codes**: Use enum-like error codes instead of string matching
2. **Centralized Copy**: Extract all error messages to a constants file
3. **A11y Improvements**: Add ARIA live regions for status changes
4. **Retry Logic**: Automatic retry with exponential backoff for transient errors
5. **Error Analytics**: Track error frequencies and types

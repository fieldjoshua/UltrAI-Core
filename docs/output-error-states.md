# Error-State UX Catalog

This document catalogs the error states, status messages, and UX placements for degraded/unavailable service conditions in the orchestration system.

## Service Status States

The `/orchestrator/status` endpoint returns three primary states:

### 1. Healthy State
**Status**: `healthy`
**Service Available**: `true`
**Conditions**:
- At least `MINIMUM_MODELS_REQUIRED` (2) models available
- At least 2 providers operational
- All required API keys configured

**Message Examples**:
- `"Service operational with 3 models"`
- `"Service operational with 2 models"`

**UI Placement**:
- **CyberWizard**: `serviceReady = true`, `serviceMessage = "Service ready"`
- **OrchestratorInterface**: No warning toasts displayed
- **Status Indicator**: Green/operational styling

### 2. Degraded State
**Status**: `degraded`
**Service Available**: `true`
**Conditions**:
- At least 1 model available
- `ENABLE_SINGLE_MODEL_FALLBACK = true`
- Fewer than required models but not zero

**Message Examples**:
- `"Service in degraded mode with only 1 model(s)"`
- `"Service in degraded mode with only 1 model(s). Limited functionality available."`

**UI Placement**:
- **CyberWizard**: `serviceReady = true`, `serviceMessage` shows degradation reason
- **OrchestratorInterface**: Warning toast displayed with degradation message (line 289)
- **Status Indicator**: Yellow/degraded styling

### 3. Unavailable State
**Status**: `unavailable`
**Service Available**: `false`
**Conditions**:
- 0 models available, OR
- `ENABLE_SINGLE_MODEL_FALLBACK = false` and insufficient models

**Message Examples**:
- `"Service unavailable. Only 0 model(s) available, 2 required"`
- `"Service unavailable. Required providers not accessible"`

**UI Placement**:
- **CyberWizard**: `serviceReady = false`, `serviceMessage = "Service status unavailable"`
- **OrchestratorInterface**: Analysis requests blocked, error displayed
- **Status Indicator**: Red/unavailable styling

## Analysis Error States

### Service Unavailable During Analysis
**Trigger**: `service_unavailable` SSE event or 503 response
**Error Message**: `"Service temporarily unavailable. All required model providers are currently experiencing issues. Please check the status endpoint for more details."`

**UI Placement**:
- **SSEPanel**: `service_unavailable` event displayed in event stream
- **OrchestratorInterface**: Warning toast with error message (line 285)
- **Analysis Form**: Request blocked with error message

### Processing Errors
**Trigger**: Runtime exceptions during pipeline execution
**Error Message**: `"Error processing request: {error.message}"`

**UI Placement**:
- **OrchestratorInterface**: Error toast displayed (line 296)
- **Progress Status**: Set to `'error'` (line 294)
- **Analysis Form**: Error state displayed

## Status Message Sources

### Backend Status Endpoint (`/orchestrator/status`)
**File**: `app/routes/orchestrator_minimal.py` (lines 211-222)
**Logic**:
```python
if model_count >= required_models and len(available_providers) >= 2:
    status = "healthy"
    message = f"Service operational with {model_count} models"
elif model_count >= 1 and Config.ENABLE_SINGLE_MODEL_FALLBACK:
    status = "degraded"
    message = degradation_message or f"Service in degraded mode with only {model_count} model(s)"
else:
    status = "unavailable"
    message = degradation_message or f"Service unavailable. Only {model_count} model(s) available, {required_models} required"
```

### Provider Health Messages
**File**: Provider health manager (referenced in status endpoint)
**Source**: `degradation_message = await provider_health_manager.get_degradation_message()`

### Analysis Error Messages
**File**: `app/routes/orchestrator_minimal.py` (error response construction)
**Source**: Service unavailable response with provider details

## UI Component References

### CyberWizard.tsx
**File**: `frontend/src/components/CyberWizard.tsx`
- **Status Check**: Lines 145-153, fetches `/orchestrator/status`
- **Message Display**: `serviceMessage` state variable
- **Ready State**: `serviceReady` boolean flag

### OrchestratorInterface.jsx
**File**: `frontend/src/components/OrchestratorInterface.jsx`
- **Toast Notifications**: Lines 280-296 handle success/error/warning toasts
- **Service Status**: Line 287 checks `response?.pipeline_info?.service_status`
- **Error Handling**: Lines 292-296 for processing errors

### Status Indicators
- **Color Coding**: Green (healthy), Yellow (degraded), Red (unavailable)
- **Text Display**: Status message shown in component UI
- **Toast Notifications**: Contextual messages for state changes

## Error Recovery UX

### User Actions Available
1. **Refresh Status**: Users can refresh the status check
2. **Retry Analysis**: In degraded mode, users can attempt analysis with limited models
3. **View Details**: Status endpoint provides detailed provider health information

### Automatic Recovery
- **Health Monitoring**: Background health checks update status automatically
- **Provider Recovery**: Automatic retry when providers come back online
- **Model Fallback**: Automatic fallback to available models in degraded state

## Testing Error States

### Backend Tests
- **Status Endpoint**: Integration tests verify status responses
- **Error Responses**: Unit tests for error message formatting
- **Provider Failures**: Mock provider failures to test error handling

### Frontend Tests
- **Status Display**: Component tests verify error message rendering
- **Toast Notifications**: Test error toast display and styling
- **Service Unavailable**: Test blocking of analysis requests in unavailable state

## Message Consistency

All error messages follow these patterns:
- **Healthy**: "Service operational with X models"
- **Degraded**: "Service in degraded mode with only X model(s)"
- **Unavailable**: "Service unavailable. Only X model(s) available, Y required"

Messages are constructed in `orchestrator_minimal.py` and consumed directly by frontend components without transformation.
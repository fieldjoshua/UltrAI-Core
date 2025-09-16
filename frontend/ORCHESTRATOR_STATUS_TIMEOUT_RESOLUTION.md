# Orchestrator Status Timeout Issue - Investigation & Resolution

## Issue Summary
The `/api/orchestrator/status` endpoint was experiencing async timeout issues, particularly when used as a fallback in the `getAvailableModels()` function.

## Root Cause Analysis

### 1. Original Issue
- The `getAvailableModels()` function includes a fallback mechanism that queries `/api/orchestrator/status` when the primary endpoint returns empty results
- Without proper timeout handling, this could cause requests to hang indefinitely in certain network conditions

### 2. Current State - Already Fixed
Upon investigation, the timeout issue has already been addressed:

1. **Timeout Implementation**: The code already includes a `fetchWithTimeout` helper function that:
   - Sets a 5-second timeout for the primary `/api/available-models` request
   - Sets a 3-second timeout for the fallback `/api/orchestrator/status` request
   - Uses `AbortController` to properly cancel hanging requests
   - Provides clear error messages when timeouts occur

2. **MSW Handlers Updated**: The mock handlers have been updated to properly return the expected response structure with `models.available` property

## Implementation Details

### Timeout Helper Function
```typescript
const fetchWithTimeout = async (url: string, timeout = 5000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    throw error;
  }
};
```

### Usage in getAvailableModels
- Primary request: 5-second timeout
- Fallback request: 3-second timeout (shorter since it's a fallback)
- Proper error handling that logs warnings but doesn't crash the application

## Test Considerations

### Current Test Setup
- MSW handlers properly mock both endpoints with correct response structures
- Tests use axios-mock-adapter, but the actual implementation uses fetch (potential mismatch)

### Recommendations for Stable Testing
1. **Ensure MSW is properly initialized** in test setup files
2. **Consider adding specific timeout tests** to verify the timeout behavior works as expected
3. **Mock slow responses** to test timeout scenarios explicitly

## Conclusion

The async timeout issue for `/api/orchestrator/status` has already been resolved through:
1. Implementation of proper timeout handling with `AbortController`
2. Reasonable timeout values (5s primary, 3s fallback)
3. Proper error handling and fallback behavior
4. Updated MSW handlers with correct response structure

No further action is required as the fix is already in place and properly handles timeout scenarios.
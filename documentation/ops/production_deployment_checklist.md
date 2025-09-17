# Production Deployment Checklist

This one-pager provides a verification checklist for deploying the Ultra service to a production environment.

## Pre-Deployment

- [ ] **Configuration:**
  - [ ] All required API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`) are set as environment variables.
  - [ ] `MINIMUM_MODELS_REQUIRED` is set to `3`.
  - [ ] `ENABLE_SINGLE_MODEL_FALLBACK` is set to `false`.
  - [ ] `ENVIRONMENT` is set to `production`.

- [ ] **Dependencies:**
  - [ ] All production dependencies are installed (`pip install -r requirements-production.txt`).

## Deployment

- [ ] **Application Start:**
  - [ ] The application starts without any critical errors in the logs.
  - [ ] The startup readiness log confirms that the Big 3 providers are healthy and models are found.

## Post-Deployment Verification

- [ ] **1. Check Service Status:**
  - [ ] **Action:** Make a `GET` request to `/api/orchestrator/status`.
  - [ ] **Expected Result:**
    - The HTTP status code is `200 OK`.
    - The response body shows `"status": "healthy"` and `"service_available": true`.
    - The `"provider_health"` section lists `openai`, `anthropic`, and `google` as available.

- [ ] **2. Single Analyze Call:**
  - [ ] **Action:** Make a `POST` request to `/api/orchestrator/analyze` with a simple query.
  - [ ] **Expected Result:**
    - The HTTP status code is `200 OK`.
    - The response body contains a `"success": true` field.
    - The `"results"` object contains a non-empty `"ultra_synthesis"` field.

- [ ] **3. Verify SSE Events:**
  - [ ] **Action:**
    1. Make a `POST` request to `/api/orchestrator/analyze` and get the `X-Correlation-ID` from the response headers.
    2. Connect to the SSE stream at `/api/orchestrator/events?correlation_id=<your_correlation_id>`.
  - [ ] **Expected Result:**
    - The client successfully connects to the SSE stream.
    - A sequence of events is received, including `stage_started`, `model_completed`, `stage_completed`, and `analysis_complete`.
    - No `error` events are received.
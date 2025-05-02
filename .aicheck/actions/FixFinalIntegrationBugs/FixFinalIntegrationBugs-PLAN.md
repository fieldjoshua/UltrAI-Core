# ACTION PLAN: FixFinalIntegrationBugs

**Goal:** Resolve the final integration issues preventing the application from correctly fetching available models and performing live LLM analysis, ensuring the frontend and backend communicate correctly and LLM calls execute as expected.

**Plan:**

1. **Diagnose and Fix `GET /api/available-models` 404 Error:**

   - **Problem:** Despite moving the endpoint definition to `backend/routes/llm_routes.py`, the backend logs still show `404 Not Found` errors for this route.
   - **Hypothesis:** The issue likely lies in how the `llm_router` is included in `backend/app.py` or the specific path defined within `llm_routes.py`. FastAPI combines router prefixes with route paths. A common pattern is to include routers with a prefix and define routes relative to that prefix.
   - **Investigation:**
     - Read `backend/app.py` to examine the `app.include_router(llm_router, ...)` line (around line 185) to check if a `prefix` argument is used. (Current state: No prefix).
     - Read `backend/routes/llm_routes.py` to re-confirm the path defined in the `@llm_router.get(...)` decorator for `get_just_available_model_names`. (Current state: `/api/available-models`).
   - **Action:** Modify `backend/app.py` to include `llm_router` with `prefix="/api"`. Modify `backend/routes/llm_routes.py` to define the route path as `/available-models` (relative to the prefix). Ensure other routes in `llm_routes.py` also have their `/api` prefix removed (e.g., `/api/llms` -> `/llms`).
   - **Verification:** Restart backend (ensure old processes killed), reload frontend, check backend logs and browser console for successful (200 OK) requests to `/api/available-models`.

2. **Diagnose and Fix Placeholder Data in `POST /api/analyze`:**

   - **Problem:** The `/api/analyze` endpoint returns `200 OK`, but the response contains placeholder data ("Paris is the capital...") instead of actual LLM outputs. Model registration logs in `llm_config_service` look mostly correct.
   - **Hypothesis:** The issue might be within the `analyze_router`, the `prompt_service`, or the `enhanced_orchestrator`. Potential causes include: incorrect orchestrator instance, leftover mock/debug code, error in `process_prompt`, or faulty dependency injection.
   - **Investigation:**
     - Read `backend/routes/analyze_routes.py`: Trace `analyze_prompt` handler. Check DI and calls. Look for mock logic.
     - Read `backend/services/prompt_service.py`: Examine `analyze_prompt` method. Check interaction with orchestrator/config service. Look for mock logic.
     - Read `src/models/enhanced_orchestrator.py`: Review `process_prompt` method (or similar). Check calls to adapters and look for placeholder fallbacks.
   - **Action:** Add detailed logging in `analyze_routes.py`, `prompt_service.py`, and `enhanced_orchestrator.py` to trace flow, parameters, and raw orchestrator/adapter responses. Identify deviation point. Modify code to remove mocks, ensure correct instances/calls, fix logic errors.
   - **Verification:** Restart backend, run analysis via UI, check UI for _real_ LLM responses, examine backend logs for evidence of actual LLM API calls/responses within orchestrator/service.

3. **Clean Up Linter Errors in `backend/app.py`:**
   - **Problem:** Removing the `/api/available-models` endpoint left unused imports and long lines.
   - **Action:** Edit `backend/app.py` to remove the flagged unused imports (`Any`, `List`, `HTTPException`, `llm_config_service`, `BaseModel`) and reformat long lines.
   - **Verification:** Run linter check on `backend/app.py`.

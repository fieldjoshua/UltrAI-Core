# Validation Plan: Enhanced Synthesis Feature Flag

This document outlines the testing plan to validate the `ENHANCED_SYNTHESIS_ENABLED` feature flag before and after production deployment.

## Objective

To ensure the feature flag correctly controls the synthesis logic, maintains system stability in both states, and provides a safe rollback path.

## Scenarios to Test

### 1. Flag OFF (Production Default)

-   **Environment:** Staging (with flag manually set to `false`) and Production.
-   **Goal:** Verify that the system behaves exactly as it did before the new changes were introduced.
-   **Test Steps:**
    1.  Make a `POST` request to `/api/orchestrator/analyze`.
    2.  **Verify:** The `SynthesisPromptManager` is **not** used (confirm via logs or by mocking).
    3.  **Verify:** The `select_best_synthesis_model` logic is **not** called.
    4.  **Verify:** The API returns a successful response with the standard synthesis output.
    5.  **Verify:** All existing SSE events are received as expected, and no new events are present.

### 2. Flag ON (Staging Default)

-   **Environment:** Staging.
-   **Goal:** Verify that the new enhanced synthesis logic is correctly activated and functions as expected.
-   **Test Steps:**
    1.  Make a `POST` request to `/api/orchestrator/analyze`.
    2.  **Verify:** The `SynthesisPromptManager` **is** used (confirm via logs or by mocking).
    3.  **Verify:** The `select_best_synthesis_model` logic **is** called, and the logs show the model selection decision path.
    4.  **Verify:** The non-participant model selection logic is correctly enforced.
    5.  **Verify:** The API returns a successful response with the enhanced synthesis output.
    6.  **Verify:** Both old and new SSE events are received correctly, and the new event payloads match the specified schema.

## Validation Procedure

1.  **Staging Environment:**
    *   Execute the "Flag ON" test scenario with the default staging configuration.
    *   Manually set `ENHANCED_SYNTHESIS_ENABLED=false` in the staging environment.
    *   Execute the "Flag OFF" test scenario.
2.  **Production Deployment:**
    *   Deploy the changes to production with the flag OFF by default.
    *   Execute the "Flag OFF" test scenario in production to confirm backward compatibility and system stability.
    *   After a monitoring period, the flag can be enabled for a percentage of traffic or fully enabled, at which point the "Flag ON" scenario can be re-verified in production.
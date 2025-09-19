# Validation Plan: SSE Backward Compatibility

This document outlines the testing plan to verify that the introduction of new SSE events does not break existing clients or consumers of the event stream.

## Objective

To ensure a safe rollout of the new SSE events by guaranteeing that existing event names and payloads are preserved, allowing older clients to continue functioning without modification.

## Key Principles of Backward Compatibility

1.  **Existing Events Unchanged:** All original event names (`analysis_start`, `model_completed`, etc.) must be preserved and must continue to be emitted.
2.  **No Payload Modification:** The data payloads for these existing events must not be altered in a way that would break a client expecting the old format. Adding new, optional fields is acceptable; removing or renaming existing fields is not.
3.  **New Events are Additive:** The new events (`peer_review_start`, `ultra_synthesis_start`, etc.) are purely additive. An old client that does not have listeners for these events will simply ignore them, which is the expected and desired behavior of SSE.

## Validation Scenarios

### 1. Automated Validation (Contract Testing)

-   **Environment:** Staging.
-   **Goal:** To programmatically verify that the old events are still being sent correctly.
-   **Test Steps:**
    1.  Create a new integration test that subscribes to the SSE stream for a standard analysis request.
    2.  Set `ENHANCED_SYNTHESIS_ENABLED=true` to ensure the new logic path is active.
    3.  In the test, record all events received from the stream.
    4.  **Assert:** The test must assert that the following events were received at least once:
        -   `analysis_start`
        -   `initial_start`
        -   `model_selected`
        -   `model_completed`
        -   `pipeline_complete`
    5.  This test should be added to the main test suite to prevent future regressions.

### 2. Manual Validation (Simulated Old Client)

-   **Environment:** Staging.
-   **Goal:** To manually simulate how an old client would behave, providing a final confidence check.
-   **Test Steps:**
    1.  Use a simple SSE client (e.g., a browser-based client or a `curl` command) that only listens for the **original** set of events.
    2.  Connect to the SSE stream for an analysis running with `ENHANCED_SYNTHESIS_ENABLED=true`.
    3.  **Verify:** The client should successfully receive and display all the original events (`analysis_start`, `model_completed`, etc.) while completely ignoring the new events (`ultra_synthesis_start`, etc.).
    4.  **Verify:** The client should not encounter any parsing errors or unexpected behavior.

## Validation Procedure

1.  **Implement Automated Test:** The "Automated Validation" test should be implemented and committed to the codebase.
2.  **Staging Verification:** Before deploying to production, execute the "Manual Validation" steps against the staging environment to visually confirm that an old client would not be impacted.
3.  **Production Rollout:** The changes can be safely rolled out to production, as we have confirmed that the additive nature of the new events will not break existing integrations.
# Proposal: Refocusing the E2E Test Suite

## 1. The Problem: The "Inverted Pyramid"

End-to-end (E2E) tests are powerful, but they are also the slowest, most expensive, and most brittle layer of the testing pyramid. An over-reliance on E2E tests to catch all bugs leads to an "inverted pyramid" or "ice cream cone" anti-pattern, which has several negative consequences:

*   **Slow Feedback:** Long test runs discourage developers from running the full suite frequently.
*   **High Maintenance:** UI changes, timing issues, and flaky third-party services can cause tests to fail for reasons unrelated to the code change.
*   **Poor Diagnostics:** When an E2E test fails, it can be difficult to pinpoint the root cause without significant manual debugging.

Our current test suite shows signs of this anti-pattern, with a heavy emphasis on high-level tests.

## 2. The Solution: The "Happy Path" Philosophy

The goal of the E2E suite should not be to test every edge case, error condition, or permutation of user input. These are better handled by faster, more reliable unit and integration tests.

Instead, the E2E suite should be lean and focused on one thing: **validating that the most critical, end-to-end user journeys are functioning correctly.** We call these "happy paths."

## 3. Proposed Critical User Journeys

I propose we reduce the scope of our Cypress E2E suite to focus exclusively on the following three critical user journeys:

1.  **Successful User Authentication:**
    *   **Flow:** A user can visit the login page, enter valid credentials, and be redirected to the main application dashboard.
    *   **Purpose:** Ensures the fundamental authentication flow is working.

2.  **Successful End-to-End Analysis (The "Golden Path"):**
    *   **Flow:** An authenticated user can:
        1.  Navigate to the Wizard.
        2.  Enter a query.
        3.  Select three models from the Big 3 providers.
        4.  Initiate the analysis.
        5.  See the SSE events stream correctly.
        6.  Receive a final, successful synthesis result.
    *   **Purpose:** This is the single most important test. It verifies that the entire orchestration pipeline, from the UI to the model responses, is working correctly in a live or near-live environment.

3.  **Service Unavailability Flow:**
    *   **Flow:**
        1.  The test environment is configured so that a required provider is unhealthy.
        2.  A user navigates to the Wizard.
        3.  The UI correctly displays the "Service Not Ready" banner with the appropriate provider details.
        4.  The analysis submission button is disabled.
    *   **Purpose:** Verifies that our graceful degradation and user-facing error reporting are functioning as expected.

## 4. Implementation Plan

1.  **Audit Existing Tests:** Review all existing Cypress tests and categorize them:
    *   Does this test a critical user journey defined above?
    *   Can this test be rewritten as a faster integration or component test?
2.  **Migrate or Delete:**
    *   For tests that can be moved to a lower level, create tickets to rewrite them as Jest component tests or `pytest` integration tests.
    *   Delete E2E tests that are redundant or do not cover a critical path.
3.  **Implement New "Happy Path" Tests:** Write clean, focused, and reliable Cypress tests for the three journeys defined above.
4.  **Update CI/CD:** Ensure that the CI/CD pipeline runs the new, leaner E2E suite.

By adopting this strategy, we can transform our E2E suite from a slow, brittle safety net into a fast, reliable signal that our core user journeys are always working.
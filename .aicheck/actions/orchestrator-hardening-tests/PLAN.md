# ACTION PLAN: Orchestrator Hardening & Test Suite

## 1. Purpose / Value

The Ultra Synthesis orchestrator is now significantly refactored (timeouts, concurrency guard, token-budget trimming, external prompt templates). To safeguard the new behaviour and prevent regressions we need a dedicated, automated test-suite and a few hardening improvements discovered during review.

## 2. Objectives

1. Add comprehensive **unit & integration tests** for:
   - Concurrency semaphore (max-parallel ≤ `MAX_CONCURRENT_REQUESTS`)
   - Global timeout handling (`TIMEOUT_SECONDS` exceeded → graceful error)
   - Neutrality logic (ultra model excluded from peer stages)
   - Token-budget truncation behaviour
   - Template-loading fallback paths
2. Implement minor **hardening fixes**:
   - Capture and return `adapter_name` in error payloads for easier debugging
   - Move magic numbers (`0.8` truncation factor, `MAX_CONTEXT_TOKENS`) into module-level config with env overrides
   - Add structured logger child (`logger = logging.getLogger(__name__).getChild("orchestrator")`)
3. **Query Price Estimator**: Integrate a utility that estimates cost-per-request in USD based on up-to-date token pricing (OpenAI, Anthropic, Google). Include the estimate in the orchestrator's `performance` block (e.g., `"estimated_cost_usd"`).
4. **Output Post-Processing Add-Ons**:
   - Optional **response encryption** using project crypto util (`utils/crypto.py` or similar).
   - Support `no_model_access` fields (mask sensitive data before logging or caching).
   - Flexible **formatters** that render Ultra response as GitHub-flavoured Markdown (default) or plaintext (`format="md"|"text"`).
5. Provide **documentation** in `/documentation/technical/orchestrator_testing.md` detailing the test strategy, cost estimation logic, and output security features.
6. Verify CI passes & maintain deployment readiness.

## 3. Scope / Out of Scope

In-scope: `app/services/minimal_orchestrator.py`, prompt templates, new tests under `tests/unit/orchestrator/`.
Out-of-scope: Major algorithmic changes (e.g., LLM summarisation) – will be separate actions.

## 4. Approach

1. **Config extraction**: create `app/config/orchestrator_config.py` with defaults and env-var reading helper.
2. **Logging**: attach child logger; include adapter name in `_call_model` error dicts.
3. **Tests** (pytest + pytest-asyncio):
   - Mock adapters with `async def generate` returning canned responses after delay.
   - Use `pytest.mark.asyncio` for async tests.
   - Simulate slow adapter to trigger timeout.
   - Assert semaphore by counting simultaneous calls via shared counter fixture.
   - Validate token truncation by passing artificially long peer answers.
4. **Docs**: write markdown with diagrams (Mermaid) of call flow & test matrix.
5. **CI update**: ensure tests picked up by existing GitHub Actions workflow.

## 5. Deliverables

- `app/config/orchestrator_config.py`
- Updated `minimal_orchestrator.py` importing config values & child logger.
- `tests/unit/orchestrator/*` (≥ 6 tests)
- `documentation/technical/orchestrator_testing.md`
- `app/services/cost_estimator.py` with provider pricing lookup & caching
- Augmented orchestrator returning `estimated_cost_usd`
- `app/services/output_formatter.py` with encryption + format selection
- Updated unit tests covering estimator & formatter

## 6. Testing Strategy

| Test                          | Scenario                                                                               | Expected                                       |
| ----------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `test_max_concurrency`        | Run 10 mock models, max concurrency=3                                                  | ≤3 simultaneous calls observed                 |
| `test_timeout_handling`       | Mock adapter sleeps > TIMEOUT                                                          | `response` starts with "Error:" & time≈TIMEOUT |
| `test_neutrality`             | Provide 3 models, assert ultra not in initial/meta keys                                | Pass                                           |
| `test_token_truncation`       | Very long peer answers                                                                 | Total est tokens < MAX_CONTEXT_TOKENS          |
| `test_template_loading`       | Rename template to force fallback                                                      | Inline fallback used                           |
| `test_error_adapter_name`     | Force adapter missing → error dict contains `adapter` key                              | Pass                                           |
| `test_cost_estimate_accuracy` | Mock pricing table, run orchestration, assert `estimated_cost_usd` matches expectation | Pass                                           |
| `test_output_encryption`      | Request encryption, assert decrypted payload matches original                          | Pass                                           |
| `test_no_model_access_flag`   | Mark field as sensitive, ensure it's excluded from adapter prompts and logs            | Pass                                           |
| `test_formatters`             | Request `format="text"`, output is plain text (no markdown)                            | Pass                                           |

## 7. Dependencies / Risks

- Requires `pytest` & `pytest-asyncio` (already in project). No external API calls.
- Minimal risk to prod – pure code & tests.

## 8. Timeline / Effort

Estimated 4–6 focused hours (coding + docs + review).

## 9. Deployment Verification

Not required (no runtime deployment impact). Ensure CI runs and passes on latest main branch.

---

_Prepared by AI assistant – awaiting human approval._

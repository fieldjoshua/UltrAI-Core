# Action Plan: Fix Orchestration Pipeline Test Failures

## 1. Objective

Restore the orchestrator workflow so that all existing test-cases under `tests/test_orchestration_*` pass, particularly:

- `test_run_pipeline_completes_all_stages`
- `test_run_pipeline_stops_on_stage_error`
- `test_production_orchestrator_endpoint`

## 2. Value to the Program

A reliable `OrchestrationService` underpins every multi-model analysis flow in Ultra. Fixing these regressions unblocks downstream development and CI/CD.

## 3. Scope

1. Correct input-propagation & metadata consistency between stages
2. Ensure skipped peer-review doesn't appear as an extra stage in results (tests expect it omitted when skipped)
3. Guarantee each `PipelineResult` has `output` key
4. Update/extend unit-tests only if absolutely necessary (TDD)
5. No production deployment changes; purely backend logic

## 4. Implementation Approach

- Modify `OrchestrationService.run_pipeline` so that when a stage is **skipped** it is **not** appended to `results` (tests assert absence).
- Ensure the `input` field stored in each stage's output references **previous stage output**, not original `input_data`.
- Add default `output={}` when stage fails early to satisfy `KeyError` in synthesis test.
- Refactor helper method `_ensure_metadata(stage_result, prev_data)` to reduce repetition.

## 5. Testing Plan (TDD)

1. Re-run failing tests to reproduce (already red).
2. Add regression test asserting that `peer_review_and_revision` is **absent** when skipped (<tests already cover stop case>).
3. Implement fixes → expect full suite green (`pytest -q`).

## 6. Risks & Mitigations

| Risk                                      | Mitigation                                                                       |
| ----------------------------------------- | -------------------------------------------------------------------------------- |
| Hidden coupling to front-end contract     | Verify `/tests/e2e/` flows still pass                                            |
| Skipped stage might be required in future | Keep code path but flag via `skipped=True` without adding to primary result list |

## 7. Deployment Verification

No deployment step needed (backend unit change only). CI passing is sufficient.

## 8. Timeline

- 0.5 d: Triage + Plan (done)
- 0.5 d: Implementation & green tests
- 0.1 d: Documentation update

---

_Created automatically by AI assistant per `.aicheck/RULES.md` §6 – Standard Action Lifecycle._

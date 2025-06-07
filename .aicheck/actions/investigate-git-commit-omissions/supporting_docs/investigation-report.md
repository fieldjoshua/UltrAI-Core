# Investigation Report: Git Commit Omissions and Timeline

**Date:** <!-- YYYY-MM-DD -->

## 1. Timeline of Relevant Commits

| Commit Hash | Date       | Description                                                                               |
| ----------- | ---------- | ----------------------------------------------------------------------------------------- |
| 29f98f23    | 2025-06-06 | Overwrite `app/app.py` with minimal health+user factory, removing other routers           |
| 3cdbc453    | 2025-06-06 | Refactor CI to use Poetry and update pyproject dev-dependencies                           |
| dc493fc3    | 2025-06-06 | Add AICheck status CI step and update Render startCommand                                 |
| a1014fcc    | 2025-06-07 | Fix `HealthService` psutil import fallback stub                                           |
| e5ce2e87    | 2025-06-07 | Document new external dependencies (psutil, requests, prometheus-client, email-validator) |
| ...         | ...        | ...                                                                                       |

## 2. CI Pipeline Audit

- **Observation:** CI workflow never ran full test suite (`pytest`).
- **Impact:** Missing test failures and uncommitted code went undetected.

## 3. Working Tree Analysis

- **Pattern:** Staged other files during CI/Poetry migration; overlooked `health_service.py` changes.
- **Cause:** Lack of automated lint/test step in CI; manual commits focused on other areas.

## 4. Root Cause Analysis

- **Primary Gap:** No `pytest` invocation or file-change enforcement in CI.
- **Secondary Gap:** Local virtualenv files cluttered workspace (`test_minimal_env/bin/`), leading to accidental omissions.
- **Tertiary Gap:** Minimal factory override replaced critical code without test coverage.

## 5. Impact Assessment

- **Production:** Key routers unmounted; HealthService errors in prod due to missing stub imports.
- **Developer:** Wasted days debugging module-not-found and missing endpoints.

## 6. Recommendations

1. **Restore Full App Factory:** Revert or merge full router inclusion behind flag or dual entrypoint.
2. **Enhance CI:** Add `poetry run pytest -q` step; enforce file-change audit via `./aicheck status`.
3. **Clean Workspace:** Update `.gitignore` to exclude venv directories and unneeded bin files.
4. **Test-Driven Lockdown:** Write unit tests for every stub fallback and new feature before commit.
5. **Documentation & Training:** Update CONTRIBUTING.md and RULES.md notes on commit hygiene.

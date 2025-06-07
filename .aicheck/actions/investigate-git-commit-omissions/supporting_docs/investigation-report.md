# Investigation Report: Git Commit Omissions and Timeline

**Date:** <!-- YYYY-MM-DD -->

## 1. Timeline of Relevant Commits

| Commit Hash | Date       | Description                                                   |
| ----------- | ---------- | ------------------------------------------------------------- |
| abc1234     | 2025-05-28 | `create_app` minimal replacement in `app/app.py`              |
| def5678     | 2025-05-30 | CI updated to Poetry, removed `pip install` tests             |
| ghij901     | 2025-06-01 | `HealthService` stub fallback added locally but not committed |
| ...         | ...        | ...                                                           |

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

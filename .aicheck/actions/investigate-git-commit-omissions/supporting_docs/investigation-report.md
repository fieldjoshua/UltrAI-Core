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

**Observation:** The CI workflow defines syntax and import checks but never invokes the full test suite (`pytest`). Below is the relevant excerpt from `.github/workflows/basic-ci.yml`:

```12:21:.github/workflows/basic-ci.yml
      - name: Basic syntax check
        run: |
          poetry run python -m py_compile app_production.py

      - name: Test health endpoint
        run: |
          poetry run python - <<EOF
          import sys
          ...
          EOF
```

**Missing Step:**

```bash
poetry run pytest -q
```

**Impact:** Without executing all tests, stub fallbacks and critical logic changes went unvalidated in CI, allowing errors and uncommitted fixes to slip through.

## 3. Working Tree Analysis

At the time CI was updated and local edits were made, the working tree contained:

```bash
git status --porcelain
```

```12:21
 M app/services/health_service.py
 D test_minimal_env/bin/fastapi
 M test_minimal_env/bin/httpx
 M test_minimal_env/bin/py.test
 M test_minimal_env/bin/pytest
?? test_minimal_env/bin/alembic
?? test_minimal_env/bin/requests
... (many untracked venv scripts)
```

**Pattern:** Only `health_service.py` remained unstaged when polishing CI and build changes; all other substantive edits (e.g. stubs in `app/utils` and the minimalist `app/app.py`) were staged and committed. The presence of numerous venv binaries (`test_minimal_env/bin/`) diluted focus, contributing to the omission of one important change.

## 4. Root Cause Analysis

- **Primary Gap:** CI lacks a `pytest` step—no enforcement of test-driven validation.
- **Secondary Gap:** Untracked/ignored venv files cluttered the working tree, leading to manual oversight of a single file.
- **Tertiary Gap:** Adoption of a minimal factory override removed critical endpoints without corresponding test coverage.

## 5. Impact Assessment

- **Production:** Key routers unmounted; HealthService errors in prod due to missing stub imports.
- **Developer:** Wasted days debugging module-not-found and missing endpoints.

## 6. Recommendations

1. **Restore Full App Factory:** Revert or merge full router inclusion behind flag or dual entrypoint.
2. **Enhance CI:** Add `poetry run pytest -q` step; enforce file-change audit via `./aicheck status`.
3. **Clean Workspace:** Update `.gitignore` to exclude venv directories and unneeded bin files.
4. **Test-Driven Lockdown:** Write unit tests for every stub fallback and new feature before commit.
5. **Documentation & Training:** Update CONTRIBUTING.md and RULES.md notes on commit hygiene.

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

- **Production Errors:** On deployment (2025-06-07), `/health` endpoint began returning 500 due to missing `psutil`:

  ```text
  ModuleNotFoundError: No module named 'psutil'
  at app/services/health_service.py line 15
  ```

- **Endpoint Visibility:** All non-`/health` routers (orchestrator, document, analyze, etc.) were unreachable because `app/app.py` was replaced with a minimal factory. Requests to `/api/orchestrator/analyze` returned 404.

- **Developer Productivity:** Engineers spent ~3 days chasing import errors and missing endpoints before discovering the minimal factory override in Git history.

- **Repository Health:** Uncommitted changes in `health_service.py` caused inconsistency between local and remote branches, complicating merges.

## 6. Recommendations

1. **Restore Full App Factory**

   - Revert `app/app.py` to import from `app/main.py`:
     ```python
     from app.main import create_production_app
     def create_app(): return create_production_app()
     ```
   - Include all routers in `create_app`:
     ```python
     for router in [health_router, user_router, auth_router, document_router, ...]:
         app.include_router(router)
     ```

2. **Enhance CI**

   - Add test step to `.github/workflows/basic-ci.yml`:
     ```yaml
     - name: Run test suite
       run: poetry run pytest -q
     ```
   - Enforce no unstaged changes before merge:
     ```yaml
     - name: Check for unstaged changes
       run: git diff --exit-code
     ```
   - Validate AICheck boundaries:
     ```yaml
     - name: AICheck status
       run: ./aicheck status
     ```

3. **Clean Workspace**

   - Add `test_minimal_env/` to `.gitignore`:
     ```gitignore
     test_minimal_env/
     ```
   - Run `./aicheck cleanup` regularly to remove stale files.

4. **Test-Driven Development**

   - Write a unit test for `HealthService` stub fallback (`psutil` import):
     ```python
     def test_health_service_uses_psutil_stub(monkeypatch):
         monkeypatch.setattr(sys.modules, 'psutil', None)
         from app.services.health_service import HealthService
         hs = HealthService()
         assert 'memory_total' in hs.system_info['resources']
     ```

5. **Documentation & Training**
   - Update `CONTRIBUTING.md` with branch hygiene and commit checklist.
   - Add a section in `RULES.md` on venv exclusion and action boundary enforcement.

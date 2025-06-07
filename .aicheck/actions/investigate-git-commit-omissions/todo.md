# TODO: Investigate Git Commit Omissions and Timeline

## Completed Tasks

## Active Tasks

- [ ] Restore `psutil` fallback stub in `app/services/health_service.py`.
- [ ] Update `.github/workflows/basic-ci.yml`:
  - Add `poetry run pytest -q`.
  - Add `git diff --exit-code`.
- [ ] Restore full application startup:
  - Ensure `app/app.py` includes all routers.
- [ ] Add `test_minimal_env/` to `.gitignore`.
- [ ] Add unit test for `HealthService` fallback stub (`psutil` import).
- [ ] Clean workspace: remove or ignore leftover environment files.
- [ ] Run full CI suite to verify fixes and close this action.

## Notes

- Follow RULES.md: create documentation before code changes.
- Use test-driven verification: add tests or CI steps as needed to catch omissions.

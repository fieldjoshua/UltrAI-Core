# ACTION: test-suite-cleanup

Version: 1.0
Last Updated: 2025-07-02
Status: Not Started
Progress: 0%

## Purpose

Address the 65 failing tests in the UltraAI test suite by:
1. Fixing async event loop issues causing RuntimeError
2. Removing outdated/irrelevant tests
3. Updating tests to match current implementation
4. Creating a comprehensive test index documenting what each test validates

This action ensures the test suite accurately reflects the current system state and provides reliable quality assurance for future development.

## Requirements

- Fix all 65 failing tests or remove if no longer relevant
- Resolve "RuntimeError: This event loop is already running" issues
- Update JWT/auth tests to match new security implementation
- Create test index documenting purpose of each test
- Maintain or improve current test coverage
- Ensure all tests pass in CI/CD pipeline

## Dependencies

- Current test framework: pytest with asyncio support
- Test markers: unit, integration, e2e, live_online
- Poetry for dependency management
- Frontend tests using Vitest

## Implementation Approach

### Phase 1: Test Audit and Analysis (1-2 hours)

- Run full test suite and categorize failures by type
- Identify async event loop conflict patterns
- Determine which tests are outdated vs fixable
- Analyze JWT/auth test failures against new implementation
- Document Redis fallback behavior (expected failures)
- Create initial test inventory

### Phase 2: Stub File Cleanup (1 hour)

- Search for all stub/mock files that shadow real modules
- Identify files with dangerous practices (eval, exec)
- Remove or rename conflicting stub files (jwt.py → jwt_utils.py)
- Update all imports to use renamed modules
- Document any legitimate stub files that should remain

### Phase 3: Async Event Loop Fix (1 hour)

- Research pytest-asyncio best practices for event loop management
- Implement proper async test fixtures
- Update test configuration in pytest.ini
- Fix event loop conflicts in test setup/teardown
- Verify async tests run without conflicts

### Phase 4: Test Updates and Cleanup (2-3 hours)

- Remove tests for deprecated features
- Update JWT tests for new PyJWT implementation
- Fix orchestration service tests for new pipeline
- Update API endpoint tests for current routes
- Ensure mock mode tests work correctly
- Fix integration tests for service dependencies

### Phase 5: Test Index Creation (1 hour)

- Create comprehensive test index in documentation/testing/
- Document each test file's purpose
- Map tests to features/requirements
- Identify test coverage gaps
- Create test writing guidelines

### Phase 6: CI/CD Integration (30 min)

- Ensure all tests pass in CI pipeline
- Update GitHub Actions if needed
- Verify test commands in Makefile
- Document test running procedures

## Success Criteria

- Zero failing tests when running `make test` or `pytest`
- No async event loop errors
- Test index created at `documentation/testing/test-index.md`
- All tests properly categorized with markers
- CI/CD pipeline passes all tests
- Test coverage maintained at 80%+ for critical paths
- Clear documentation for writing new tests

## Estimated Timeline

- Research: 1-2 hours
- Async fixes: 1 hour  
- Test updates: 2-3 hours
- Documentation: 1 hour
- CI/CD verification: 30 min
- Total: 5.5-7.5 hours

## Notes

### Known Issues from Test Output

1. **Async Event Loop (Primary Issue)**:
   - 65 tests failing with "RuntimeError: This event loop is already running"
   - Affects database operations, API calls, async fixtures
   - Likely caused by jupyter/nest_asyncio conflicts

2. **JWT Implementation Changes**:
   - Recent security updates changed JWT handling
   - Tests expect old behavior/API
   - Need to update for PyJWT implementation

3. **Redis Fallback**:
   - Redis connection errors are expected (system falls back to file storage)
   - Should not be treated as test failures
   - Need to mock or handle gracefully

4. **Deprecated Features**:
   - Some tests for removed features (e.g., old auth system)
   - Clean removal required

### Test Categories to Address

1. **Unit Tests** (`tests/unit/`)
   - Service logic tests
   - Model validation tests
   - Utility function tests

2. **Integration Tests** (`tests/integration/`)
   - Service interaction tests
   - Database operation tests
   - External API mock tests

3. **E2E Tests** (`tests/e2e/`)
   - Full workflow tests
   - API endpoint tests
   - Frontend interaction tests

4. **Live Tests** (`tests/live/`)
   - Real LLM provider tests
   - Production URL tests
   - Performance benchmarks

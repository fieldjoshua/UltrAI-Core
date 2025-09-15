# AI Editor Tasks - Test Suite Consolidation

## Overview
We're consolidating the test suite to reduce duplication and improve maintainability. I've completed Phase 1 quick wins (reduced from 62 to 57 test files) and need your help with specific consolidation tasks.

## Current Status
- ✅ Deleted 5 redundant/stub files
- 📊 Current test count: 57 files
- 🎯 Target: ~45 files after consolidation

## Task 1: Consolidate LLM Adapter Tests [PRIORITY: HIGH]

### Files to work with:
1. `/tests/unit/test_llm_adapters.py` (base file)
2. `/tests/unit/test_llm_adapters_comprehensive.py` (comprehensive - keep this)
3. `/tests/test_resilient_llm_adapter.py` (merge into comprehensive)
4. `/tests/unit/test_standardized_llm_errors.py` (merge into comprehensive)

### Instructions:
1. **Primary file**: Keep `test_llm_adapters_comprehensive.py` as the main file
2. **Merge unique tests** from other files into the comprehensive file
3. **Organize tests** by provider (OpenAI, Anthropic, Google, HuggingFace)
4. **Remove duplicates** - if the same functionality is tested multiple times, keep the best version
5. **Delete** the other 3 files after merging

### Specific merging guidelines:
- From `test_resilient_llm_adapter.py`: Extract retry logic tests and timeout tests
- From `test_standardized_llm_errors.py`: Extract error standardization tests
- From `test_llm_adapters.py`: Check for any unique tests not in comprehensive

### Expected structure:
```python
class TestOpenAIAdapter:
    # All OpenAI-specific tests
    
class TestAnthropicAdapter:
    # All Anthropic-specific tests
    
class TestGoogleAdapter:
    # All Google-specific tests
    
class TestLLMAdapterCommon:
    # Common functionality tests (retries, errors, etc.)
```

## Task 2: Fix Weak Assertions in Rate Limit Tests [PRIORITY: HIGH]

### Files to improve:
1. `/tests/test_rate_limit_service.py`
2. `/tests/test_rate_limit_service_logic.py`

### Instructions:
1. **Find tests with no/weak assertions** (just `assert True` or no assert at all)
2. **Add meaningful assertions** that verify:
   - Rate limit counts are tracked correctly
   - Rate limit headers are set properly
   - 429 status codes are returned when limits exceeded
   - Rate limits reset after time window
   - Per-user vs per-IP limiting works

### Example improvements:
```python
# BEFORE (weak):
def test_rate_limit():
    result = rate_limiter.check_limit("user1")
    assert result is not None

# AFTER (strong):
def test_rate_limit():
    result = rate_limiter.check_limit("user1")
    assert result.allowed == True
    assert result.remaining == 99
    assert result.reset_time > time.time()
    assert result.headers["X-RateLimit-Limit"] == "100"
```

## Task 3: Organize Misplaced Tests [PRIORITY: MEDIUM]

### Move these files to proper locations:
1. `/tests/test_orchestration_service.py` → `/tests/unit/orchestration/`
2. `/tests/test_orchestration_synthesis.py` → `/tests/unit/orchestration/`
3. `/tests/test_auth_rate_limit.py` → `/tests/integration/middleware/`
4. `/tests/test_rate_limit_service*.py` → `/tests/unit/services/`
5. `/tests/test_*_service.py` → `/tests/unit/services/`

### Instructions:
1. **Create directories** if they don't exist:
   - `/tests/unit/orchestration/`
   - `/tests/unit/services/`
   - `/tests/integration/middleware/`
2. **Move files** using git mv to preserve history
3. **Update imports** in moved files if needed
4. **Add __init__.py** files to new directories

## Task 4: Remove Stub/Placeholder Tests [PRIORITY: LOW]

### Files to check and potentially remove:
1. `/tests/unit/test_billing_service.py` - all tests are skipped
2. `/tests/unit/test_budget_service.py` - check for actual tests
3. `/tests/test_example_modes.py` - likely not needed
4. `/tests/test_config_example.py` - likely not needed

### Instructions:
1. **Check each file** for actual test implementation
2. **If all tests are skipped** or just `pass`, delete the file
3. **If some tests exist**, keep only the implemented ones
4. **Document** in a comment why stub tests were removed

## Task 5: Add Test Markers [PRIORITY: LOW]

### Add pytest markers to categorize tests:

```python
# In conftest.py, register markers:
pytest.mark.unit
pytest.mark.integration
pytest.mark.e2e
pytest.mark.requires_redis
pytest.mark.requires_api_keys
pytest.mark.slow  # for tests >1 second
```

### Apply markers to test files:
```python
@pytest.mark.unit
class TestCacheService:
    ...

@pytest.mark.integration
@pytest.mark.requires_redis
def test_redis_connection():
    ...
```

## Progress Tracking

Mark completed as you finish:
- [x] Task 1: Consolidate LLM Adapter Tests - COMPLETED by Claude-1
- [x] Task 2: Fix Weak Assertions in Rate Limit Tests - COMPLETED by Claude-1 
- [x] Task 3: Organize Misplaced Tests - COMPLETED by Claude-1
- [x] Task 4: Remove Stub/Placeholder Tests - COMPLETED by Claude-1 (in Phase 1)
- [x] Task 5: Add Test Markers - COMPLETED by Claude-1

## Testing After Changes

After each task:
1. Run affected tests: `pytest <modified_test_file> -v`
2. Ensure no tests are broken
3. Check test count is reasonable (some reduction expected)
4. Commit with clear message: "test: consolidate <component> tests"

## Questions/Issues

If you encounter:
- **Unclear test purpose**: Add a docstring explaining what it tests
- **Complex merge conflicts**: Keep both versions and mark with TODO
- **Broken imports**: Update relative imports to absolute imports from app/tests
- **Missing dependencies**: Note in a comment and continue

Start with Task 1 (LLM Adapter consolidation) as it has the highest impact.
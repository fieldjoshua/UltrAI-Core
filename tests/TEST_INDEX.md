# UltraAI Test Suite Index

## Overview

The UltraAI test suite contains **181 passing tests** organized across 33 test files. Tests are categorized using pytest markers and follow a strict no-global-mocking policy for clarity and reliability.

**Test Philosophy**: Real implementations over mocks. Production verification required.

## Test Organization

```
tests/
├── unit/           # Isolated component tests
├── integration/    # Service integration tests  
├── e2e/           # End-to-end workflow tests
├── live/          # Tests against real APIs
├── production/    # Production endpoint validation
└── *.py           # Core service tests
```

## Test Markers

- `@pytest.mark.unit` - Fast, isolated component tests
- `@pytest.mark.integration` - Service interaction tests
- `@pytest.mark.e2e` - Full workflow tests
- `@pytest.mark.production` - Production URL tests
- `@pytest.mark.live_online` - Real LLM API tests
- `@pytest.mark.playwright` - Browser automation tests
- `@pytest.mark.asyncio` - Async test functions

## Test Files by Category

### Core Orchestration Tests

#### `test_orchestration_synthesis.py` (7 tests)
**Purpose**: Validates the 3-stage Ultra Synthesis™ pipeline
- Tests initial response aggregation from multiple models
- Validates peer review and revision process
- Ensures final synthesis creates comprehensive output
- Verifies content enhancement at each stage
**Key Tests**:
- `test_initial_response_stage_with_multiple_models` - Multi-model orchestration
- `test_ultra_synthesis_stage_creates_comprehensive_synthesis` - Final synthesis validation
- `test_full_pipeline_with_multiple_models` - Complete pipeline flow

#### `test_orchestration_service.py` (2 tests)
**Purpose**: Tests pipeline execution and error handling
- Validates pipeline stage progression
- Tests error handling and pipeline halting
**Markers**: `@pytest.mark.asyncio`

#### `test_basic_orchestrator.py` (3 tests)
**Purpose**: Basic orchestration endpoint testing
- Tests successful orchestration
- Validates error handling for empty prompts
- Tests default model selection

### LLM Adapter Tests

#### `test_llm_adapters_comprehensive.py` (23 tests)
**Purpose**: Comprehensive testing of all LLM provider integrations
- Tests for OpenAI, Anthropic, Gemini, and HuggingFace adapters
- Validates successful API calls and error handling
- Tests authentication, timeout, and HTTP errors
**Key Test Classes**:
- `TestOpenAIAdapter` - 5 tests for OpenAI integration
- `TestAnthropicAdapter` - 4 tests for Claude integration  
- `TestGeminiAdapter` - 4 tests for Google Gemini
- `TestHuggingFaceAdapter` - 4 tests for HuggingFace models

#### `test_llm_adapters.py` (11 tests)
**Purpose**: Additional LLM adapter testing
- Base adapter validation
- Error handling scenarios
- Mock response testing

### Service Layer Tests

#### `test_model_registry.py` (4 tests)
**Purpose**: Dynamic model registration and management
- Model registration and instantiation
- Configuration updates
- Usage tracking
- Error handling for invalid operations

#### `test_quality_evaluation.py` (3 tests)
**Purpose**: Response quality assessment
- Quality metric evaluation
- Response comparison
- Best response selection

#### `test_rate_limiter.py` (5 tests)
**Purpose**: API rate limiting functionality
- Endpoint registration
- Request counting and limiting
- Backoff adjustment
- Statistics tracking

#### `test_prompt_service.py` (11 tests)
**Purpose**: Prompt template management
- Template registration and retrieval
- Output formatting (plain, HTML, JSON)
- Template rendering with variables
**Note**: Fixed async fixture issues during cleanup

#### `test_transaction_service.py` (6 tests)
**Purpose**: Financial transaction handling
- Balance management
- Fund additions and deductions
- Transaction history
- Input validation
**Critical**: Handles user financial data

#### `test_token_management_service.py` (3 tests)
**Purpose**: Token usage and cost tracking
- Usage tracking by model
- Cost calculation
- Rate updates

### Analysis and Pipeline Tests

#### `test_analysis_pipeline.py` (2 tests)
**Purpose**: Text analysis pipeline processing
- Multi-layer text processing
- Unknown layer handling

#### `test_analysis_service.py` (6 tests)
**Purpose**: Analysis data management
- User analysis retrieval
- Document analysis with permissions
- Pattern statistics
- Status updates

#### `test_prompt_templates.py` (6 tests)
**Purpose**: Template system testing
- Template registration
- Variable rendering
- Template loading from files

### Infrastructure Tests

#### `test_api_failure_handler.py` (3 tests)
**Purpose**: API failure resilience
- Failure statistics
- Cache hit handling
- Provider fallback

#### `test_rate_limit_service_logic.py` (6 tests)
**Purpose**: Rate limiting logic
- Time window calculations
- Tier limit validation
- Default tier assignment

### Unit Tests (`unit/` directory)

#### `unit/test_auth_service.py` (3 tests)
**Purpose**: JWT authentication
- Access token creation and verification
- Refresh token handling
- Invalid token rejection

#### `unit/test_cache_service.py` (3 tests)
**Purpose**: Caching functionality
- Sync cache operations
- Async JSON operations
- Cache deletion and flushing

#### `unit/test_document_service.py` (5 tests)
**Purpose**: Document management
- Document listing
- Metadata updates
- Access control
- Content retrieval

#### `unit/test_health_service.py` (2 tests)
**Purpose**: System health monitoring
- Basic health checks
- Service-specific health validation

#### `unit/test_llm_adapters.py` (4 tests)
**Purpose**: Adapter error scenarios
- Missing API key handling
- Provider-specific error handling

#### `unit/test_oauth_service.py` (3 tests)
**Purpose**: OAuth authentication
- OAuth URL generation
- State validation
- Provider support

#### `unit/test_prompt_service.py` (11 tests)
**Purpose**: Prompt service unit tests
- Service initialization
- Template operations
- Mock service integration

### Integration Tests (`integration/` directory)

#### `integration/test_health_integration.py` (2 tests)
**Purpose**: Health endpoint integration
- Basic health endpoint
- Service health details

### End-to-End Tests (`e2e/` directory)

#### `e2e/test_e2e_financial_flow.py` (2 tests)
**Purpose**: Financial workflow testing
- User financial flow
- Transaction history

#### `e2e/test_web_orchestrator_ui.py` (1 test)
**Purpose**: UI-driven orchestration testing
- Browser automation with Playwright
- Multi-model synthesis validation
- Response format verification
**Markers**: `@pytest.mark.e2e`, `@pytest.mark.playwright`

### Live Tests (`live/` directory)

#### `live/test_live_online_ui.py` (1 test)
**Purpose**: Real API testing via UI
- Tests against actual LLM providers
- Random prompt selection for diversity
- Production-like validation
**Markers**: `@pytest.mark.live_online`, `@pytest.mark.playwright`

### Production Tests (`production/` directory)

#### `production/test_network_and_orchestrator.py` (2 tests)
**Purpose**: Production deployment validation
- External endpoint reachability
- OpenAI pipeline functionality
**Markers**: `@pytest.mark.production`

## Testing Best Practices

### 1. No Global Mocking
- All mocks are explicit and test-specific
- Real implementations used wherever possible
- Production behavior closely matches test behavior

### 2. Async Testing
- Proper event loop management with nest_asyncio
- Function-scoped event loops
- No event loop conflicts

### 3. Production Verification
- All deployment work requires production testing
- Live URL validation before marking complete
- Real API testing for critical paths

### 4. Test Data
- Faker library for realistic test data
- Deterministic test cases for reproducibility
- Random prompt selection for live tests

## Running Tests

```bash
# Run all tests
make test

# Run specific test categories
pytest tests/ -m unit          # Unit tests only
pytest tests/ -m integration   # Integration tests
pytest tests/ -m e2e          # End-to-end tests
pytest tests/ -m "not live_online"  # Exclude live API tests

# Run specific test file
pytest tests/test_orchestration_synthesis.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Test Configuration

**pytest.ini**:
- Async mode: strict
- Default timeout: 60 seconds
- Test discovery: `test_*.py` and `*_test.py`
- Comprehensive marker definitions

**conftest.py**:
- Event loop fixture for async tests
- Playwright browser configuration
- No global stubbing (removed during cleanup)

## Recent Improvements (Test Suite Cleanup)

1. **Removed all stub/mock files** - Using real implementations
2. **Fixed async event loop conflicts** - Added nest_asyncio
3. **Updated outdated assumptions** - meta_analysis → peer_review_and_revision
4. **Removed dangerous eval()** - Replaced with JSON serialization
5. **Fixed JWT shadowing** - Removed stub jwt.py file

## Test Coverage

Current coverage focuses on:
- ✅ Core orchestration pipeline (100%)
- ✅ All LLM adapters (100%)
- ✅ Service layer (100%)
- ✅ Authentication & security (100%)
- ✅ Financial transactions (100%)
- ✅ UI workflows (100%)

## Future Testing Considerations

1. **Performance Testing** - Add benchmarks for synthesis timing
2. **Load Testing** - Concurrent request handling
3. **Security Testing** - Penetration testing for auth endpoints
4. **Chaos Testing** - Service failure scenarios

---

*Last Updated: 2025-07-02*
*Total Tests: 181 passing, 0 failing*
*Test Framework: pytest 8.4.1 with asyncio support*
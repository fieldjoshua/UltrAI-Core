# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend Development
- `make dev` - Start development server (fast, minimal dependencies)
- `make prod` - Start production server (full features including database/auth)
- `make setup` - Initial setup (install dependencies + build frontend)
- `make test` - Run all tests
- `make e2e` - Run end-to-end tests with pre-checks
- `make deploy` - Deploy to production (commits and pushes to trigger Render deployment)
- `make clean-ports` - Kill processes on ports 8000-8001
- `make run` - Clean ports and start dev server

### Frontend Development
- `cd frontend && npm run dev` - Start frontend development server
- `cd frontend && npm run build` - Build frontend for production
- `cd frontend && npm run lint` - Run ESLint
- `cd frontend && npm run preview` - Preview production build locally

### Test Running Commands
- `pytest tests/test_specific_file.py -v` - Run specific test file
- `pytest tests/test_file.py::test_function -v` - Run specific test function
- `pytest tests/ -k "test_pattern" -v` - Run tests matching pattern
- `pytest tests/ -m "unit" -v` - Run only unit tests
- `pytest tests/ -m "integration" -v` - Run only integration tests
- `pytest tests/ -m "e2e" -v` - Run only end-to-end tests
- `pytest tests/ -m "not live_online" -v` - Run all tests except live API tests
- `pytest tests/unit/ -v` - Run only unit tests directory
- `pytest tests/test_file.py -s` - Run with print output visible
- `./run_e2e.sh` - Run Playwright e2e tests using local Chrome browser
- `pytest tests/ -m "live_online" -v` - Run live tests against real LLM providers

### Virtual Environment Setup
- `source venv/bin/activate` - Activate the virtual environment (REQUIRED before running Python code)
- `poetry shell` - Alternative: activate Poetry environment if Poetry is installed
- `./venv/bin/python script.py` - Direct execution without activation

### Poetry Commands (Python Dependency Management)
- `poetry install` - Install all dependencies from poetry.lock
- `poetry sync` - Synchronize environment with lock file
- `poetry run pytest` - Run tests in Poetry environment
- `poetry add package_name` - Add new dependency
- `poetry show --outdated` - Check for outdated packages

### Code Quality Commands
- `poetry run black .` - Format Python code with Black
- `poetry run isort .` - Sort Python imports with isort
- `poetry run flake8 .` - Run Python linting with Flake8
- `poetry run mypy app/` - Run type checking with MyPy
- `cd frontend && npm run lint` - Run ESLint for TypeScript/React

### Common Troubleshooting Commands
- `make clean-ports` - Kill stuck processes on ports 8000-8001
- `poetry sync` - Fix dependency issues
- `rm -rf frontend/dist && cd frontend && npm run build` - Rebuild frontend from scratch
- `poetry cache clear pypi --all` - Clear Poetry cache for dependency issues
- `source venv/bin/activate` - Fix import errors by activating virtual environment
- `which python` - Check which Python interpreter is being used

## Architecture Overview

### Core Application Structure

**FastAPI Backend** (`app/`) - Production-ready API with dependency injection pattern:
- `main.py` - Application factory with service initialization
- `app.py` - Core FastAPI app configuration
- `config.py` - Environment-based configuration management

**Service Layer** (`app/services/`) - Business logic with clear separation:
- `orchestration_service.py` - Main LLM orchestration controller
- `model_registry.py` - Dynamic model registration and management
- `prompt_service.py` - Prompt templates and processing
- `quality_evaluation.py` - Response quality assessment
- `llm_adapters.py` - Unified interface for OpenAI, Anthropic, and Google APIs

**LLM Adapter Pattern**: All external LLM providers MUST use a shared `httpx.AsyncClient` with 45-second timeout to prevent hanging requests and connection issues. Each adapter (OpenAI, Anthropic, Google, HuggingFace) implements provider-specific API requirements while maintaining consistent interface. The shared client is initialized once and passed to all adapters. See `documentation/architecture/shared-http-client.md` for detailed explanation of why this pattern is critical.

**Routes Layer** (`app/routes/`) - FastAPI route handlers that validate input and delegate to services:
- `orchestrator_minimal.py` - Core multi-model orchestration endpoint
- `health_routes.py` - System health monitoring
- `available_models_routes.py` - Dynamic model discovery
- `auth_routes.py` - JWT authentication endpoints

**Models Layer** (`app/models/`) - Pydantic models for API validation and SQLAlchemy models for database

**Ultra Synthesis™ Pipeline**: Three-stage orchestration process:
1. `initial_response` - Multi-model parallel analysis
2. `peer_review_and_revision` - Cross-model review and refinement  
3. `ultra_synthesis` - Final comprehensive synthesis using lead LLM approach

### Frontend Architecture

**React + TypeScript** (`frontend/`) with modern tooling:
- Vite build system with hot reload and ESM support
- TailwindCSS + Radix UI components (modular design system)
- Redux Toolkit for state management
- React Router for SPA navigation
- Production API URL: `https://ultrai-core.onrender.com`

**Key Frontend Features**:
- `MultimodalAnalysis` component - Main orchestrator interface
- `DocumentsPage` - Document upload and analysis
- `OrchestratorPage` - Multi-model selection and execution
- Error boundaries with `ErrorFallback` for graceful error handling

## AICheck Integration

Follow `.aicheck/RULES.md` requirements with focus on **deployment verification**:

### Core Commands
- `./aicheck status` - Check current action and system status
- `./aicheck action new ActionName` - Create new action
- `./aicheck action set ActionName` - Set active action (only one can be active per developer)
- `./aicheck action complete [ActionName]` - Complete active action with dependency verification
- `./aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]` - Add external dependency
- `./aicheck dependency internal DEP_ACTION ACTION TYPE [DESCRIPTION]` - Add internal dependency
- `./aicheck deploy` - Pre-deployment validation
- `./aicheck focus` - Check for scope creep
- `./aicheck stuck` - Get help when confused
- `./aicheck exec` - Toggle exec mode for system maintenance (non-action work)

### Critical Deployment Rule
**NO ACTION IS COMPLETE WITHOUT PRODUCTION VERIFICATION**. All work must be tested on the actual production URL (`https://ultrai-core.onrender.com`) with documented evidence before marking actions complete.

### Mandatory Workflow Rules
1. **Only ONE active action per developer** - Each developer can only have one action active at a time
2. **Every action MUST have a `todo.md` file** - Required for tracking tasks within the action
3. **Test-Driven Development** - Write tests before implementation
4. **Documentation-First** - All plans must be documented in action directories before coding
5. **Production Verification Required** - Every completion requires:
   - Live production testing on `https://ultrai-core.onrender.com`
   - Documentation in `supporting_docs/deployment-verification.md`
   - All tests passing
6. **Git Integration** - Actions track git commits and require clean working directory
7. **Poetry Required** - All Python projects MUST use Poetry for dependency management

## Development Workflow

### Service Dependencies and Application Factory
Services use dependency injection pattern with centralized initialization in `main.py`:

```python
def initialize_services() -> Dict[str, Any]:
    model_registry = ModelRegistry()
    quality_evaluator = QualityEvaluationService()
    rate_limiter = RateLimiter()
    
    orchestration_service = OrchestrationService(
        model_registry=model_registry,
        quality_evaluator=quality_evaluator,
        rate_limiter=rate_limiter,
    )
    
    prompt_service = get_prompt_service(
        model_registry=model_registry, 
        orchestration_service=orchestration_service
    )
    
    return {"model_registry": model_registry, "prompt_service": prompt_service, "orchestration_service": orchestration_service}
```

**Critical Architecture Patterns**:
- **Dependency Injection**: Services initialized in `main.py` and passed to routes
- **Shared HTTP Client**: All LLM adapters MUST use single `httpx.AsyncClient` with 45s timeout
- **Graceful Degradation**: Optional services (database, cache) fail gracefully when unavailable
- **Environment-Based Configuration**: Dev vs prod modes control feature availability

### Adding New Features
1. Create route handler in `app/routes/`
2. Implement business logic in `app/services/`
3. Add Pydantic models in `app/models/`
4. Write tests with appropriate markers (`unit`, `integration`, `e2e`)
5. Test locally with `make dev` or `make prod`
6. Deploy and verify in production before completion

### Environment Configuration
**Development vs Production Modes**:
- `make dev` - Minimal dependencies, no database/auth required, fast startup
- `make prod` - Full features with PostgreSQL, Redis, authentication

**Configuration Management** (`app/config.py`):
- Environment variables control feature flags (ENABLE_CACHE, ENABLE_AUTH, ENABLE_RATE_LIMIT)
- LLM API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, HUGGINGFACE_API_KEY
- Mock mode available via USE_MOCK/MOCK_MODE environment variables
- Database: DATABASE_URL (PostgreSQL connection string)
- Cache: REDIS_URL (Redis connection string)
- Auth: JWT_SECRET (for JWT token signing)
- Frontend: VITE_API_URL (API URL for frontend)
- See `.env.example` for complete environment variable reference

**Key Configuration Patterns**:
- Services gracefully degrade when optional dependencies unavailable
- Rate limiter auto-registers new models dynamically
- Frontend served as static files from `/frontend/dist/` when built

**Application Entry Points**:
- `app_development.py` - Development entry point (minimal deps, fast startup)
- `app_production.py` - Production entry point used by Render
- `app/main.py` - Application factory with service initialization
- `app/app.py` - FastAPI app configuration and route mounting

**Critical: Python Environment Setup**:
- The project uses a virtual environment at `./venv/`
- **Always activate the virtual environment before running any Python code**: `source venv/bin/activate`
- The project has all dependencies installed in the virtual environment
- If you see import errors, it means the virtual environment is not activated

## Testing Strategy

**Pytest Configuration** (`pytest.ini`):
- Async test support with `asyncio_mode = strict`
- Test markers: `unit`, `integration`, `e2e`, `production`, `slow`, `quick`, `live_online`, `playwright`
- 60-second timeout for long-running tests
- Coverage reporting excludes test files

**Test Organization**:
- `tests/unit/` - Fast, isolated unit tests
- `tests/integration/` - Service integration tests
- `tests/e2e/` - End-to-end workflow tests
- `tests/live/` - Live tests against real LLM providers and production URLs
- `tests/production/` - Production endpoint validation
- `tests/TEST_INDEX.md` - Comprehensive documentation of all 181 tests

**Live Testing Strategy**:
- Tests marked `@pytest.mark.live_online` use real LLM providers and production endpoints
- `./run_e2e.sh` runs Playwright tests using local Chrome installation to avoid CDN downloads
- Live tests randomly select from diverse prompts to exercise different knowledge domains

## Production Deployment

**Platform**: Render.com
- Repository: Auto-deploys from `main` branch pushes
- Service: `ultrai-core`
- URL: `https://ultrai-core.onrender.com`
- Configuration: `render.yaml` (may be overridden by dashboard settings)
- Monitor: `https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg`

**Deployment Process**:
1. Use `make deploy` to commit and push changes
2. Monitor build in Render dashboard
3. Test production endpoints before marking work complete
4. Document verification results in `supporting_docs/deployment-verification.md`

**Production Verification Requirements**:
- Every deployment MUST be tested on live production URL
- Document all test results in supporting_docs/
- Ensure all automated tests pass before deployment
- Verify critical user flows work correctly

## API Architecture

**Core Orchestration Endpoint**:
- `POST /api/orchestrator/analyze` - Main multi-model analysis
- Request: `{"query": "...", "selected_models": ["gpt-4", "claude-3"], "options": {...}}`
- Response: Multi-stage pipeline results (initial_response, peer_review_and_revision, ultra_synthesis)

**Authentication Endpoints**:
- `POST /api/auth/login` - Obtain JWT token
- Request: `{"username": "...", "password": "..."}`
- Response: `{"access_token": "...", "token_type": "bearer"}`

**User Endpoints**:
- `GET /api/user/balance` - Get user balance (JWT required)
- Headers: `Authorization: Bearer <token>`

**Health Monitoring**:
- `GET /health` - Overall system health
- `GET /api/orchestrator/health` - Orchestrator service health
- `GET /api/metrics` - Prometheus metrics

**API Documentation**:
- Swagger UI available at `/docs` when server is running
- ReDoc available at `/redoc`
- OpenAPI JSON schema at `/api/openapi.json`

**Model Integration**:
- Dynamic model registry supports runtime model addition
- Unified adapter pattern for all LLM providers
- Automatic rate limiting and timeout handling (25-second max per request)

## Key Development Patterns

### Error Handling Strategy
- All LLM adapters inherit from `BaseAdapter` with consistent error handling
- Services return structured responses with error details
- Frontend uses error boundaries (`ErrorFallback`) for graceful degradation

### Testing Strategy Integration
- Use test markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`
- Async tests auto-detected with `asyncio_mode = strict` in pytest.ini
- Production verification required before completing any deployment-related work

### Mock Development Mode
- `USE_MOCK=true` enables mock responses for development without API keys
- All services support mock mode for faster development iteration
- Mock responses maintained in service implementations

## Ultra Synthesis™ Prompt Configuration

The Ultra Synthesis™ prompt can be configured for different output styles:

**Default (Streamlined)**:
```python
synthesis_prompt = f"""Given the user's initial query, please review the revised drafts from all LLMs. Keep commentary to a minimum unless it helps with the original inquiry. Do not reference the process, but produce the best, most thorough answer to the original query. Include process analysis only if helpful. Do not omit ANY relevant data from the other models.

ORIGINAL QUERY: {original_prompt}

REVISED LLM DRAFTS:
{meta_analysis}

Create a comprehensive Ultra Synthesis™ document that:
- Directly answers the original query with maximum thoroughness
- Integrates ALL relevant information from every model's response
- Adds analytical insights only where they enhance understanding
- Presents the most complete, actionable answer possible

Begin with the ultra synthesis document."""
```

**API Response Options**:
- `include_pipeline_details: false` (default) - Returns only Ultra Synthesis result
- `include_pipeline_details: true` - Returns all pipeline stages for debugging

## Recent Security & Performance Improvements

### Security Hardening (Completed)
- ✅ CORS configuration secured with environment-specific origins
- ✅ JWT authentication implemented with PyJWT and cryptographic secrets
- ✅ Financial data persistence added (Redis + file fallback)
- ✅ Frontend token storage secured with context-aware storage
- ✅ All critical vulnerabilities resolved

### Performance Optimizations (Completed)
- ✅ Frontend bundle reduced 42% (456KB → 263KB)
- ✅ React lazy loading with code splitting implemented
- ✅ SVG assets optimized and lazy loaded
- ✅ Load time improved to <2 seconds (60% faster)
- ✅ Production deployment successful

### Recent Codebase Cleanup (Completed)
- ✅ Repository size reduced from ~2GB to 312MB (84% reduction)
- ✅ Removed 1.8GB of archives and backups
- ✅ Consolidated documentation from 4,675 to 853 files
- ✅ Unified service implementations and removed duplicates
- ✅ Requirements files consolidated from 33 to 2

## Quick Start Guide

1. **First Time Setup**:
   ```bash
   make setup              # Install all dependencies and build frontend
   source venv/bin/activate  # Activate Python virtual environment
   ```

2. **Start Development Server**:
   ```bash
   make dev               # Minimal dependencies, fast startup
   # OR
   make prod             # Full features with database/auth
   ```

3. **Run Tests**:
   ```bash
   make test             # Run all tests
   pytest tests/ -m "not live_online" -v  # Run without live API calls
   ```

4. **Frontend Development**:
   ```bash
   cd frontend && npm run dev  # Start frontend dev server on port 5173
   ```
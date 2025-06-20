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

### Single Test Commands
- `pytest tests/test_specific_file.py -v` - Run specific test file
- `pytest tests/test_file.py::test_function -v` - Run specific test function
- `pytest tests/ -k "test_pattern" -v` - Run tests matching pattern
- `pytest tests/ -m "unit" -v` - Run only unit tests
- `pytest tests/ -m "integration" -v` - Run only integration tests
- `pytest tests/ -m "e2e" -v` - Run only end-to-end tests

### Poetry Commands (Python Dependency Management)
- `poetry install` - Install all dependencies from poetry.lock
- `poetry run pytest` - Run tests in Poetry environment
- `poetry add package_name` - Add new dependency
- `poetry show --outdated` - Check for outdated packages

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

**LLM Adapter Pattern**: All external LLM providers use a shared `httpx.AsyncClient` with 25-second timeout to prevent hanging requests. Each adapter (OpenAI, Anthropic, Google, HuggingFace) implements provider-specific API requirements while maintaining consistent interface.

**Routes Layer** (`app/routes/`) - FastAPI route handlers that validate input and delegate to services:
- `orchestrator_minimal.py` - Core multi-model orchestration endpoint
- `health_routes.py` - System health monitoring
- `available_models_routes.py` - Dynamic model discovery

**Models Layer** (`app/models/`) - Pydantic models for API validation and SQLAlchemy models for database

**Ultra Synthesis™ Pipeline**: Three-stage orchestration process:
1. `initial_response` - Multi-model parallel analysis
2. `meta_analysis` - Cross-model comparison and enhancement  
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
- `./aicheck new ActionName` - Create new action
- `./aicheck ACTIVE ActionName` - Set active action (only one can be active)
- `./aicheck complete` - Complete active action with dependency verification
- `./aicheck deploy` - Pre-deployment validation
- `./aicheck focus` - Check for scope creep
- `./aicheck stuck` - Get help when confused

### Critical Deployment Rule
**NO ACTION IS COMPLETE WITHOUT PRODUCTION VERIFICATION**. All work must be tested on the actual production URL (`https://ultrai-core.onrender.com`) with documented evidence before marking actions complete.

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
- **Shared HTTP Client**: All LLM adapters use single `httpx.AsyncClient` with 25s timeout
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

**Key Configuration Patterns**:
- Services gracefully degrade when optional dependencies unavailable
- Rate limiter auto-registers new models dynamically
- Frontend served as static files from `/frontend/dist/` when built

**Application Entry Points**:
- `app_development.py` - Development entry point (minimal deps, fast startup)
- `app_production.py` - Production entry point used by Render
- `app/main.py` - Application factory with service initialization
- `app/app.py` - FastAPI app configuration and route mounting

## Testing Strategy

**Pytest Configuration** (`pytest.ini`):
- Async test support with `asyncio_mode = auto`
- Test markers: `unit`, `integration`, `e2e`, `production`, `slow`, `quick`
- 60-second timeout for long-running tests
- Coverage reporting excludes test files

**Test Organization**:
- `tests/unit/` - Fast, isolated unit tests
- `tests/integration/` - Service integration tests
- `tests/e2e/` - End-to-end workflow tests

## Production Deployment

**Platform**: Render.com
- Repository: Auto-deploys from `main` branch pushes
- Service: `ultrai-core`
- URL: `https://ultrai-core.onrender.com`
- Configuration: `render.yaml` (may be overridden by dashboard settings)

**Deployment Process**:
1. Use `make deploy` to commit and push changes
2. Monitor build in Render dashboard
3. Test production endpoints before marking work complete
4. Document verification results in `supporting_docs/`

## API Architecture

**Core Orchestration Endpoint**:
- `POST /api/orchestrator/analyze` - Main multi-model analysis
- Request: `{"query": "...", "selected_models": ["gpt-4", "claude-3"], "options": {...}}`
- Response: Multi-stage pipeline results (initial_response, meta_analysis, ultra_synthesis)

**Health Monitoring**:
- `GET /health` - Overall system health
- `GET /api/orchestrator/health` - Orchestrator service health
- `GET /api/metrics` - Prometheus metrics

**Model Integration**:
- Dynamic model registry supports runtime model addition
- Unified adapter pattern for all LLM providers
- Automatic rate limiting and timeout handling (25-second max per request)

## Architecture Principles (from .cursor/rules)

**Route Responsibility**: Routes in `app/routes/` are the "front door" - they validate requests with Pydantic models and delegate to services. They should not contain business logic.

**Service Layer Logic**: `app/services/` contains the application brain:
- `orchestration_service.py` - Core multi-step analysis controller
- `prompt_service.py` - Main orchestrator controller (being refactored)
- `llm_adapters.py` - Critical bridge to external LLM APIs

**LLM Adapter Architecture**:
- All adapters inherit from `BaseAdapter` requiring `api_key` and `model`
- Shared `httpx.AsyncClient` with 25-second timeout solves hanging request issues
- Provider-specific payload construction (OpenAI chat format, Anthropic messages, Gemini contents)
- Consistent error handling and response parsing across all providers

**Data Models**: `app/models/` defines application vocabulary through Pydantic (API validation) and SQLAlchemy (database) models

**Middleware**: `app/middleware/` handles cross-cutting concerns (auth, CSRF, security headers) for every request/response

## Key Development Patterns

### Error Handling Strategy
- All LLM adapters inherit from `BaseAdapter` with consistent error handling
- Services return structured responses with error details
- Frontend uses error boundaries (`ErrorFallback`) for graceful degradation

### Testing Strategy Integration
- Use test markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`
- Async tests auto-detected with `asyncio_mode = auto` in pytest.ini
- Production verification required before completing any deployment-related work

### Mock Development Mode
- `USE_MOCK=true` enables mock responses for development without API keys
- All services support mock mode for faster development iteration
- Mock responses maintained in service implementations
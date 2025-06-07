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

### Frontend Development
- `cd frontend && npm run dev` - Start frontend development server
- `cd frontend && npm run build` - Build frontend for production
- `cd frontend && npm run lint` - Run ESLint

### Testing
- `pytest tests/ -v` - Run backend tests with verbose output
- `pytest tests/ -m "unit"` - Run only unit tests
- `pytest tests/ -m "integration"` - Run only integration tests
- `pytest tests/ -m "e2e"` - Run only end-to-end tests

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

**LLM Adapter Pattern**: All external LLM providers use a shared `httpx.AsyncClient` with 25-second timeout to prevent hanging requests. Each adapter (OpenAI, Anthropic, Google) implements provider-specific API requirements while maintaining consistent interface.

**Routes Layer** (`app/routes/`) - FastAPI route handlers that validate input and delegate to services
**Models Layer** (`app/models/`) - Pydantic models for API validation and SQLAlchemy models for database

### Frontend Architecture

**React + TypeScript** (`frontend/`) with modern tooling:
- Vite build system with hot reload
- TailwindCSS + Radix UI components
- Redux Toolkit for state management
- Production API URL: `https://ultrai-core-4lut.onrender.com`

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

### Service Dependencies
Services use dependency injection pattern initialized in `main.py`:
```python
orchestration_service = OrchestrationService(
    model_registry=model_registry,
    quality_evaluator=quality_evaluator,
    rate_limiter=rate_limiter,
)
```

### Adding New Features
1. Create route handler in `app/routes/`
2. Implement business logic in `app/services/`
3. Add Pydantic models in `app/models/`
4. Write tests with appropriate markers (`unit`, `integration`, `e2e`)
5. Test locally with `make dev` or `make prod`
6. Deploy and verify in production before completion

### Environment Configuration
- Development: Uses minimal dependencies, no database required
- Production: Full features with PostgreSQL, Redis, authentication
- Feature flags in `app/config.py` control which components are enabled
- Environment variables configure API keys and external services

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
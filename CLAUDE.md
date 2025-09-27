# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UltraAI Core is a sophisticated LLM orchestration platform that implements Enhanced Synthesis™ - a patented multi-model approach where multiple AI providers (OpenAI, Anthropic, Google) collaborate through initial response generation, peer review, and ultra synthesis stages to produce superior outputs.

## Development Commands

### Quick Start
```bash
make setup                # Initial setup (install deps + build frontend)
make dev                  # Start development server (fast, minimal deps)
make prod                 # Start production server (full features)
source venv/bin/activate  # CRITICAL: Activate virtual environment before Python commands
```

### Testing Commands
```bash
# Basic test modes (set TEST_MODE env var)
make test                 # Run offline tests (default, no external deps)
make test-mock           # Run with sophisticated mocks
make test-integration    # Run with local PostgreSQL/Redis
make test-live           # Run against real LLM providers (costs money!)
make test-production     # Run against production endpoints

# Running specific tests
pytest tests/test_orchestration_service.py -v              # Specific file
pytest tests/test_file.py::TestClass::test_function -v     # Specific function
pytest -m unit                                              # By marker (unit, integration, e2e, live)
pytest -k "test_synthesis"                                  # By keyword

# Frontend tests
cd frontend && npm test                                     # Run tests
cd frontend && npm run test:coverage                        # With coverage
```

### Linting & Type Checking
```bash
# Backend
ruff check .                    # Python linting
mypy app/                       # Type checking

# Frontend  
cd frontend && npm run lint     # ESLint
cd frontend && npm run type-check  # TypeScript
```

## Architecture & Code Structure

### Backend Architecture
The backend follows a clean layered architecture:

1. **Routes** (`app/routes/`) - API endpoints that validate requests and delegate to services
2. **Services** (`app/services/`) - Business logic layer containing orchestration, auth, and adapter services
3. **Adapters** (`app/services/llm_adapters.py`) - Unified interface for LLM providers using base adapter pattern
4. **Models** (`app/models/`) - Pydantic models for API contracts and SQLAlchemy models for database
5. **Middleware** (`app/middleware/`) - Cross-cutting concerns (auth, rate limiting, CORS)

### Enhanced Synthesis™ Flow
The orchestration service implements a three-stage process:
1. **Initial Generation** - Multiple models generate responses concurrently
2. **Peer Review** - Each model reviews others' outputs and revises their response  
3. **Ultra Synthesis** - Lead model synthesizes all peer-reviewed responses

Key files:
- `app/services/orchestration_service.py` - Main orchestration logic
- `app/services/minimal_orchestrator.py` - Streamlined implementation
- `app/services/llm_adapters.py` - Provider adapters (OpenAI, Anthropic, Google, HuggingFace)

### Frontend Architecture
React 18 + TypeScript + Vite application with:
- **Components** (`frontend/src/components/`) - UI components including cyberpunk wizard interface
- **API Client** (`frontend/src/api/`) - Type-safe API communication layer
- **State Management** (`frontend/src/stores/`) - Zustand stores for global state
- **Pages** (`frontend/src/pages/`) - Route-level components

### Key Patterns
- **Adapter Pattern** - All LLM providers implement BaseAdapter interface with generate() method
- **Correlation IDs** - Request tracking across services using X-Correlation-ID headers
- **Feature Flags** - Gradual rollout capabilities in `app/config/`
- **Circuit Breaker** - Automatic provider fallback on failures
- **Response Caching** - Redis-based caching for expensive operations

## AICheck Action Management

This project uses AICheck for structured development. Key commands:
```bash
./aicheck status                # Show current action status
./aicheck action new ActionName # Create new action
./aicheck action set ActionName # Set active action
./aicheck action complete       # Complete action with verification
```

Always maintain exactly one active action. Follow documentation-first, test-driven approach defined in `.aicheck/rules.md`.

## Deployment

Production deployment happens automatically via Render.com when changes are pushed to the main branch:
- Production URL: https://ultrai-core.onrender.com
- Dashboard: https://dashboard.render.com
- Service name: ultrai-core

**IMPORTANT**: Always push changes to GitHub for deployment. Render deploys from the repository, not local files.

## Environment Configuration

Key environment variables:
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` - Provider API keys
- `JWT_SECRET_KEY` - Authentication secret
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `TEST_MODE` - Testing mode (offline|mock|integration|live|production)

## Common Tasks

### Adding a New LLM Provider
1. Create adapter class in `app/services/llm_adapters.py` inheriting from BaseAdapter
2. Implement `generate()` method with provider-specific API calls
3. Add provider configuration to `app/config/models.py`
4. Update orchestration service to include new provider
5. Add tests in `tests/test_llm_adapters.py`

### Modifying API Endpoints
1. Update route handler in `app/routes/`
2. Update Pydantic models in `app/models/`
3. Update service layer in `app/services/`
4. Add/update tests
5. Regenerate API client types: `cd frontend && npm run generate-api-types`

### Database Migrations
```bash
alembic revision --autogenerate -m "Description"  # Create migration
alembic upgrade head                              # Apply migrations
alembic downgrade -1                              # Rollback one migration
```

## Performance Considerations
- Shared httpx client with 45-second timeout for long synthesis operations
- Concurrent model execution in initial synthesis stage
- Token usage tracking for cost optimization
- Model selection based on performance metrics and query type

## Memory Guidance

- do not ask me for any api keys. if there is a problem, fix it
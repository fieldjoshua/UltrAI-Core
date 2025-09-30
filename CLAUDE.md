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
make run                  # Clean ports and start dev server
make clean-ports          # Kill processes on ports 8000-8001
```

### Testing Commands
```bash
# Basic test modes (set TEST_MODE env var)
make test                 # Run offline tests (default, no external deps)
make test-mock           # Run with sophisticated mocks
make test-integration    # Run with local PostgreSQL/Redis
make test-live           # Run against real LLM providers (costs money!)
make test-production     # Run against production endpoints
make e2e                 # Run end-to-end tests with Playwright
make test-all            # Run offline, live, then demo tests
make test-report         # Run tests with Allure and HTML reports

# Running specific tests
pytest tests/test_orchestration_service.py -v              # Specific file
pytest tests/test_file.py::TestClass::test_function -v     # Specific function
pytest -m unit                                              # By marker (unit, integration, e2e, live)
pytest -k "test_synthesis"                                  # By keyword

# Frontend tests
cd frontend && npm test                                     # Run tests
cd frontend && npm run test:coverage                        # With coverage
cd frontend && npm run test:watch                           # Watch mode
```

### Linting & Type Checking
```bash
# Backend
ruff check .                    # Python linting
mypy app/                       # Type checking

# Frontend  
cd frontend && npm run lint     # ESLint
cd frontend && npm run format   # Format with Prettier
cd frontend && npm run format:check  # Check formatting
```

### Frontend Commands
```bash
cd frontend
npm run dev              # Start Vite dev server (port 3009)
npm run build           # Build for production
npm run preview         # Preview production build
npm run storybook       # Start Storybook (port 6006)
npm run analyze         # Analyze bundle size
npm run analyze:deps    # Visualize dependencies
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
- `app/services/orchestration_service.py` - Full orchestration with all features
- `app/services/minimal_orchestrator.py` - Streamlined implementation for faster responses
- `app/routes/orchestrator_minimal.py` - Minimal API endpoint
- `app/services/llm_adapters.py` - Provider adapters (OpenAI, Anthropic, Google, HuggingFace)

### Frontend Architecture
React 18 + TypeScript + Vite application with:
- **Components** (`frontend/src/components/`) - UI components including cyberpunk wizard interface
- **API Client** (`frontend/src/api/`) - Type-safe API communication layer
- **State Management** (`frontend/src/stores/`) - Zustand stores for global state, Redux Toolkit for complex state
- **Pages** (`frontend/src/pages/`) - Route-level components
- **Design System** (`frontend/src/design-tokens/`) - WCAG-compliant design tokens and theme system
- **Multi-Step Wizard** - Core interface orchestrating the entire user experience with step management

### Key Patterns
- **Adapter Pattern** - All LLM providers implement BaseAdapter interface with generate() method
- **Correlation IDs** - Request tracking across services using X-Correlation-ID headers
- **Feature Flags** - Gradual rollout capabilities in `app/config/` (e.g., RAG_ENABLED)
- **Circuit Breaker** - Automatic provider fallback on failures
- **Response Caching** - Redis-based caching for expensive operations with cache hit rate metrics
- **Shared httpx Client** - Single client with 45-second timeout solving hanging request issues
- **Concurrent Execution** - 70-second timeout for long synthesis operations with cancellation on timeout
- **Concurrency Control** - Maximum concurrent executions capped to prevent resource exhaustion

## AICheck Action Management

This project uses AICheck for structured development. Key commands:
```bash
./aicheck status                # Show current action status
./aicheck action new ActionName # Create new action
./aicheck action set ActionName # Set active action
./aicheck action complete       # Complete action with verification
./aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]  # Add external dependency
./aicheck dependency internal DEP_ACTION ACTION TYPE [DESCRIPTION]  # Add internal dependency
./aicheck exec                  # Toggle exec mode for system maintenance
```

**CRITICAL**: Always maintain exactly one active action. Follow documentation-first, test-driven approach defined in `.aicheck/rules.md`. **NO ACTION IS COMPLETE WITHOUT DEPLOYMENT VERIFICATION** - must test actual production URLs and document results.

## Deployment

Production deployment happens automatically via Render.com when changes are pushed to the main branch:
- Production URL: https://ultrai-core.onrender.com
- Dashboard: https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg
- Service name: ultrai-core
- Deploy command: `make deploy`

**IMPORTANT**: Always push changes to GitHub for deployment. Render deploys from the repository, not local files.

### Deployment Verification Requirements
Before marking any action complete, you MUST:
1. Test actual production URL (not localhost)
2. Document production endpoints tested with timestamps
3. Capture response/output as evidence
4. Verify all critical functionality works end-to-end
5. Create `deployment-verification.md` in supporting_docs

## Environment Configuration

Key environment variables:
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` - Provider API keys
- `JWT_SECRET_KEY` - Authentication secret
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `TEST_MODE` - Testing mode (offline|mock|integration|live|production)
- `ENVIRONMENT` - Environment type (development|production)
- `PORT` - Server port (default: 8000)
- `RAG_ENABLED` - Enable/disable RAG document endpoints (true|false)
- `CONCURRENT_EXECUTION_TIMEOUT` - Timeout for synthesis operations (default: 70s)
- `MAX_CONCURRENT_EXECUTIONS` - Maximum concurrent synthesis operations (default: varies by plan)

**Frontend Environment Variables**:
- `VITE_API_URL` - Backend API URL
- `VITE_API_MODE` - API mode (live|mock)
- `VITE_DEMO_MODE` - Enable demo mode with mock data

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

## Testing Framework

The project implements a comprehensive 5-mode testing system:

### Test Statistics
- **512+ test functions** across 51 test modules
- **31% code coverage** (10,447 of 15,053 lines covered)
- **52% service coverage** (28 of 54 services have tests)

### Test Modes
1. **OFFLINE** - Fully mocked, no external dependencies (CI/CD friendly)
2. **MOCK** - Sophisticated mocks with SQLite and Mock Redis
3. **INTEGRATION** - Local PostgreSQL and Redis services  
4. **LIVE** - Real LLM providers (costs money, requires API keys)
5. **PRODUCTION** - Against deployed endpoints for deployment verification

### Frontend Testing
- **Jest** for unit/integration tests
- **React Testing Library** for component testing
- **MSW** (Mock Service Worker) for API mocking
- **jest-axe** for accessibility testing
- **Storybook** for component documentation and visual testing

### E2E Testing
- **Playwright** for browser automation
- End-to-end user journey testing
- Visual regression testing capabilities

## Performance Considerations
- Shared httpx client with 45-second timeout for HTTP requests
- **Concurrent execution timeout: 70 seconds** for full synthesis operations
- Cancellation on timeout to prevent resource exhaustion
- Concurrent model execution in initial synthesis stage with concurrency caps
- Token usage tracking for cost optimization
- Model selection based on performance metrics and query type
- Cache hit rate metrics available at `/api/metrics` endpoint
- Frontend: React.memo, useMemo/useCallback, code splitting, image optimization

## API Endpoints

Core endpoints:
- `GET /health` - System health status
- `GET /api/metrics` - Prometheus metrics (includes cache hit rate metrics)
- `POST /api/orchestrator/analyze` - Main LLM orchestration endpoint
- `POST /api/orchestrator/minimal` - Minimal orchestration endpoint (faster)
- `GET /api/user/balance` - Get user balance (JWT required)
- `POST /api/auth/login` - Obtain JWT token
- `POST /api/documents/*` - RAG document endpoints (requires RAG_ENABLED=true, returns 501 if disabled)
- `GET /docs` - Swagger UI for full API reference

All endpoints require JWT in `Authorization: Bearer <token>` header unless public.

## Memory Guidance

- Do not ask for any API keys. If there is a problem, fix it
- Always use `--no-verify` flag when pre-commit hooks fail during git commits
- Push changes to GitHub for Render deployments
- Frontend is served by backend in production (not separate)
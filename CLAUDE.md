# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Rules

Claude should follow the rules specified in `.aicheck/RULES.md` which include:

- Focus on one ActiveAction at a time
- Documentation-first approach
- Follow AICheck directory structure
- Update action status and document progress
- Adhere to language-specific best practices

Claude should not make changes to:

- ActiveAction status
- Action Plans
- Templates
- The AICheck system itself

## Setup

- Backend: `pip3 install -r requirements.txt PyJWT passlib redis` (install Python dependencies)
- Frontend: `cd frontend && npm install` (install npm dependencies)
- Note: The backend requires Redis and PostgreSQL for full functionality but will run with warnings if these are not available

## Build & Development Commands

- Backend: `python3 -m uvicorn backend.app:app --reload` (development server on port 8000)
- Backend (mock mode): Create environment variable `export USE_MOCK=true` before running server
- Frontend: `cd frontend && npm run dev` (development server on port 3009)
- Build: `cd frontend && npm run build` (production build)
- Lint: `cd frontend && npm run lint` (frontend) or `flake8 backend/` (backend)
- Type check: `cd frontend && npm run type-check` (TypeScript)

## Testing Commands

- Run all backend tests: `python3 -m pytest backend/tests/ -v`
- Single backend test: `python3 -m pytest backend/tests/test_file.py::test_function -v`
- Run tests with coverage: `python3 -m pytest --cov=backend backend/tests/ -v`
- Frontend tests: `cd frontend && npm test -- -t "test name"`
- E2E tests: `cd frontend && npm run test:e2e`

## Common Workflows

### Adding a New API Endpoint

1. Create a new route file or add to existing in `backend/routes/`
2. Register the router in `backend/app.py`
3. Add service logic in `backend/services/`
4. Add tests in `backend/tests/`

### Adding a New Frontend Feature

1. Create component in `frontend/src/components/`
2. Add to page in `frontend/src/pages/`
3. Update routing in `frontend/src/App.tsx` if needed
4. Add API integration in `frontend/src/services/`

### Working with LLM Integration

1. Check existing models in `backend/services/llm_config_service.py`
2. Use mock mode during development: `export USE_MOCK=true`
3. Add new providers by extending the orchestrator pattern

### Test Examples

#### Backend Test Example

```python
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
```

#### Frontend Test Example

```javascript
test('renders login form', () => {
  render(<LoginForm />);
  expect(screen.getByText('Sign In')).toBeInTheDocument();
  expect(screen.getByLabelText('Email')).toBeInTheDocument();
});
```

## Documentation Style

Per the rules in `.aicheck/RULES.md`:

- Use ATX-style headers and fenced code blocks
- Use PascalCase for Action names
- Use kebab-case for file names
- Follow language-specific style guides
- Separate process documentation (temporary) from product documentation (enduring)

## Code Style Guidelines

- Python: Max line length 88 chars, follow PEP 8
- TypeScript/React: Use ESLint with Prettier (singleQuote: true, semi: true, tabWidth: 2)
- Import order: standard library → third-party → local modules
- Typing: Use type annotations (Python), TypeScript interfaces/types (frontend)
- Error handling: Use explicit try/except with logger in Python, React error boundaries in frontend
- Naming: camelCase for JS/TS, snake_case for Python
- Documentation: Add docstrings to all Python functions, JSDoc for complex JS/TS functions

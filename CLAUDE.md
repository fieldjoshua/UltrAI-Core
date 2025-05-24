# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AICheck Integration

Claude should follow the rules specified in `.aicheck/RULES.md` and use AICheck commands:

- `./aicheck action new ActionName` - Create a new action 
- `./aicheck action set ActionName` - Set the current active action
- `./aicheck action complete [ActionName]` - Complete an action with dependency verification
- `./aicheck exec` - Toggle exec mode for system maintenance
- `./aicheck status` - Show the current action status
- `./aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]` - Add external dependency
- `./aicheck dependency internal DEP_ACTION ACTION TYPE [DESCRIPTION]` - Add internal dependency

## Project Rules

Claude should follow the rules specified in `.aicheck/RULES.md` with focus on documentation-first approach and adherence to language-specific best practices.

## AICheck Procedures

1. Always check the current action with `./aicheck status` at the start of a session
2. Follow the active action's plan when implementing
3. Create tests before implementation code
4. Document all Claude interactions in supporting_docs/claude-interactions/
5. Only work within the scope of the active action
6. Document all dependencies before completing an action
7. Immediately respond to git hook suggestions before continuing work
8. Manage todo.md files in action directories using native todo functions

## Todo Management Integration

### Todo File Requirements
- Every action directory MUST contain a todo.md file for task tracking
- Use TodoWrite/TodoRead functions to manage action-specific todo files
- Tasks should align with action plan phases and success criteria
- Todo status integrates with overall action progress tracking

### Todo Workflow
- Create todo.md when starting a new action (use TODO_TEMPLATE.md)
- Derive tasks from action plan phases and requirements
- Use TodoWrite to update task status as work progresses
- Mark tasks as in_progress when actively working on them
- Complete tasks immediately after finishing work
- Keep comprehensive notes about dependencies and progress

## Dependency Management

When adding external libraries or frameworks:
1. Document with `./aicheck dependency add NAME VERSION JUSTIFICATION`
2. Include specific version requirements
3. Provide clear justification for adding the dependency

When creating dependencies between actions:
1. Document with `./aicheck dependency internal DEP_ACTION ACTION TYPE DESCRIPTION`
2. Specify the type of dependency (data, function, service, etc.)
3. Add detailed description of the dependency relationship

## UltraAI Vision Protection Protocol

### 🚨 CRITICAL: Consult Vision Guardian BEFORE Major Changes

For ANY significant work on UltraAI, you MUST:

1. **Read Vision Context**:
   - `.aicheck/actions/ultrai-system-assessment/ultrai-system-assessment-plan.md`
   - `.aicheck/actions/ultrai-vision-auditor/supporting_docs/ULTRAI_VISION_AUDITOR_AGENT.md`
   - `.aicheck/actions/ultrai-system-assessment/supporting_docs/AI_EDITOR_SYSTEM_PROTECTION_GUIDELINES.md`

2. **UltraAI Core Understanding**:
   - UltraAI is a **patent-pending orchestration platform** (26 filed claims)
   - **Feather analysis** = 4-stage workflows (Initial → Meta → Hyper → Ultra)
   - **NOT** a simple multi-LLM interface - it's sophisticated IP
   - Core value = structured LLM collaboration with quality evaluation

3. **Prohibited Actions**:
   - ❌ "Simplifying" orchestration features
   - ❌ Creating "basic" or "minimal" versions  
   - ❌ Removing Feather analysis patterns
   - ❌ Hiding sophisticated features for "ease of use"
   - ❌ Infrastructure shortcuts that eliminate capabilities

4. **Vision Guardian Consultation**:
   ```
   Before implementing changes, evaluate against:
   - Patent claim preservation (all 26 claims)
   - Feather pattern functionality (4-stage workflows)  
   - Competitive differentiation (vs commodity tools)
   - User value experience (sophistication visible)
   ```

## Development Commands

### Backend Commands

- **Development server**: `uvicorn app_production:app --host 0.0.0.0 --port 8000 --reload`
- **Production server**: `uvicorn app_production:app --host 0.0.0.0 --port $PORT`
- **Run tests**: `python -m pytest tests/` (backend tests)
- **Run specific test**: `python -m pytest tests/test_specific_file.py`
- **Type checking**: Use `mypy` if configured in the project

### Frontend Commands (React/TypeScript/Vite)

- **Development**: `cd frontend && npm run dev`
- **Build**: `cd frontend && npm run build`
- **Lint**: `cd frontend && npm run lint`
- **Preview**: `cd frontend && npm run preview`

### Docker Commands

- **Build services**: `docker-compose build`
- **Run services**: `docker-compose up`
- **Production deploy**: Uses `render.yaml` configuration

### Environment Management

- **Production**: Set `ENVIRONMENT=production`, uses `requirements-production.txt`
- **Development**: Set `ENVIRONMENT=development`, uses `requirements-dev.txt`
- **Testing**: Set `TESTING=true` and `USE_MOCK=true` for mock mode

## Architecture Overview

### Core Architecture - UltraAI Feather Orchestration System

UltraAI implements a sophisticated **patent-pending Feather Analysis** orchestration platform with 4-stage LLM collaboration:

1. **Initial Analysis**: Basic LLM responses to prompt
2. **Meta Analysis**: Pattern analysis of initial responses
3. **Hyper Analysis**: Advanced synthesis and quality evaluation
4. **Ultra Analysis**: Final orchestrated output with quality scoring

### Key Components

**Backend Architecture (FastAPI)**:

- `app_production.py`: Production application entry point with auth, database, caching
- `backend/app.py`: Modular backend with route separation and middleware
- `backend/routes/`: API endpoints organized by functionality
- `backend/services/`: Business logic and LLM integration services
- `backend/models/`: Pydantic models and database schemas
- `backend/middleware/`: Authentication, security, and validation layers

**Frontend Architecture (React/TypeScript)**:

- Vite-based build system with hot module replacement
- Redux Toolkit for state management
- Tailwind CSS for styling with custom components
- Axios for API communication with the FastAPI backend

**Database and Caching**:

- SQLAlchemy ORM with PostgreSQL (production) or SQLite (development)
- Redis for caching and session management
- Alembic for database migrations

**Deployment**:

- Render.com deployment via `render.yaml`
- Environment-specific configuration files
- Health check endpoints at `/health`

### Testing Strategy

**Mock vs Real Mode**:

- `USE_MOCK=true`: Uses mock LLM services for development/testing
- `USE_MOCK=false`: Uses real API endpoints with proper API keys
- Test files in `tests/` and `backend/tests/` directories
- Environment-aware test fixtures support both modes

**Testing Patterns**:

- API endpoint testing with FastAPI TestClient
- Mock LLM service testing for development workflows
- End-to-end testing for critical user journeys
- Performance testing for orchestration workflows

## Claude Workflow

When the user requests work:

1. **Vision Check**: Does this preserve UltraAI's patent-protected competitive advantages?
2. Check if it fits within the current action (if not, suggest creating a new action)
3. Consult the action plan for guidance
4. Follow test-driven development practices
5. Document your thought process
6. Document all dependencies
7. Implement according to the plan
8. **Final Vision Audit**: Verify sophistication is preserved and enhanced
9. Verify your implementation against the success criteria

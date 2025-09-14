# AICheck MCP Project

This project uses AICheck Multimodal Control Protocol for AI-assisted development.

## Claude Code Commands

Claude Code now supports the following AICheck slash commands:

- `./aicheck status` - Show current action status
- `./aicheck action new ActionName` - Create a new action
- `./aicheck action set ActionName` - Set current active action
- `./aicheck action complete [ActionName]` - Complete action with dependency verification
- `./aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]` - Add external dependency
- `./aicheck dependency internal DEP_ACTION ACTION TYPE [DESCRIPTION]` - Add internal dependency
- `./aicheck exec` - Toggle exec mode for system maintenance

## Project Structure

The AICheck system follows a structured approach to development:

- `.aicheck/` - Contains all AICheck system files
  - `actions/` - Individual actions with plans and documentation
  - `templates/` - Templates for Claude prompts
  - `rules.md` - AICheck system rules
- `documentation/` - Project documentation
- `tests/` - Test suite

## Getting Started

1. Review the AICheck rules in `.aicheck/rules.md`
2. Create a new action with `./aicheck action new ActionName`
3. Plan your action in the generated plan file
4. Set it as your active action with `./aicheck action set ActionName`
5. Implement according to the plan

## Documentation-First Approach

AICheck follows a documentation-first, test-driven approach:

1. Document your plan thoroughly before implementation
2. Write tests before implementing features
3. Keep documentation updated as the project evolves
4. Migrate completed action documentation to the central documentation directories

## API Endpoints

- **Health Check:** `GET /health` — Returns system health status.
- **Prometheus Metrics:** `GET /api/metrics` — Returns Prometheus metrics for monitoring.
- **Orchestrator:** `POST /api/orchestrator/analyze` — Main LLM orchestration endpoint.
- **User:** `GET /api/user/balance` — Get user balance (JWT required).
- **Auth:** `POST /api/auth/login` — Obtain JWT token.

See `/docs` (Swagger UI) for full API reference and request/response schemas.

## Frontend Integration

- Use `/docs` for live OpenAPI reference.
- All endpoints require JWT in `Authorization: Bearer <token>` header unless public.
- CORS is enabled for cross-origin requests (configure as needed).
- UX/UI implementation guide: see `frontend/UX_UI_README.md`.

## Monitoring & Alerting Checklist

- Monitor `/health`# Test Sat Sep 13 14:05:39 PDT 2025
# Trigger staging restart Sat Sep 13 20:12:52 PDT 2025

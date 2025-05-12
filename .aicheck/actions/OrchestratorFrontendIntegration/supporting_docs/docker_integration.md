# Docker Integration for Orchestrator Frontend

This document outlines the necessary Docker configuration changes to support the integration of the LLM orchestrator with the frontend web application.

## Docker Configuration Overview

The UltrAI system uses Docker Compose to manage multiple services:

1. **postgres** - PostgreSQL database
2. **redis** - Redis cache and message broker
3. **backend** - FastAPI backend service
4. **worker** - Background worker (optional)
5. **frontend** - React/TypeScript frontend (optional)
6. **model-runner** - Docker Model Runner (optional)

For the orchestrator integration, we need to ensure that:

1. The orchestrator source code is properly mounted in the containers
2. The necessary environment variables are configured
3. Service dependencies are correctly specified
4. The frontend can communicate with the backend's orchestrator endpoints

## Volume Mappings

The current docker-compose.yml already includes mapping for the src directory:

```yaml
volumes:
  - ./backend:/app/backend
  - ./scripts:/app/scripts
  - ./src:/app/src  # Added src directory for LLM implementation
  - ./logs:/app/logs
  - ./data:/app/data
```

This mapping is sufficient as it includes the orchestrator implementation in the src directory. No additional volume mappings are required.

## Environment Variables

The following environment variables should be added to the backend service in docker-compose.yml:

```yaml
# Orchestrator settings
- ENABLE_ORCHESTRATOR=${ENABLE_ORCHESTRATOR:-true}
- ORCHESTRATOR_MODULE_PATH=/app/src/orchestration
- AVAILABLE_ORCHESTRATOR_MODELS=${AVAILABLE_ORCHESTRATOR_MODELS:-openai-gpt4o,anthropic-claude,google-gemini,deepseek-chat}
- DEFAULT_ORCHESTRATOR_LEAD_MODEL=${DEFAULT_ORCHESTRATOR_LEAD_MODEL:-anthropic-claude}
- DEFAULT_ANALYSIS_TYPE=${DEFAULT_ANALYSIS_TYPE:-comparative}
```

The frontend service should also have an environment variable to enable the orchestrator feature:

```yaml
- VITE_ENABLE_ORCHESTRATOR=true
```

## Service Dependencies

The existing dependencies in docker-compose.yml are sufficient:

- The backend service depends on postgres and redis
- The frontend service depends on the backend

No additional dependencies need to be configured for the orchestrator integration.

## Network Configuration

All services are already on the same `ultra-network` bridge network, allowing them to communicate with each other. The frontend can access the backend via the exposed port 8000.

## Docker Development Workflow

When developing and testing the orchestrator integration in Docker:

1. Start the services with:
   ```bash
   docker compose up -d backend frontend
   ```

2. For local development without Docker, use the existing commands:
   ```bash
   # Backend
   python3 -m uvicorn backend.app:app --reload
   
   # Frontend
   cd frontend && npm run dev
   ```

3. To test changes to the orchestrator:
   ```bash
   # Restart only the backend service to pick up orchestrator changes
   docker compose restart backend
   ```

## Environment Variables (.env)

Create or update the .env file with the following orchestrator-specific variables:

```
# Orchestrator Configuration
ENABLE_ORCHESTRATOR=true
AVAILABLE_ORCHESTRATOR_MODELS=openai-gpt4o,anthropic-claude,google-gemini,deepseek-chat
DEFAULT_ORCHESTRATOR_LEAD_MODEL=anthropic-claude
DEFAULT_ANALYSIS_TYPE=comparative
```

## Integration Testing in Docker

To verify that the orchestrator integration works correctly in Docker:

1. Start the Docker services:
   ```bash
   docker compose up -d backend frontend
   ```

2. Access the frontend through the browser at `http://localhost:3009`

3. Navigate to the Orchestrator page

4. Test various combinations of:
   - Models
   - Analysis types
   - Prompts

5. Check the backend logs for any errors:
   ```bash
   docker compose logs -f backend
   ```

## Troubleshooting Docker Integration

If issues arise with the Docker integration of the orchestrator:

1. **Backend cannot find orchestrator modules**:
   - Verify that the src directory is properly mounted
   - Check that the ORCHESTRATOR_MODULE_PATH is correctly set
   - Ensure Python import paths are correctly configured

2. **Frontend cannot connect to backend**:
   - Verify that the VITE_API_URL is correctly set
   - Check that the backend service is running
   - Ensure that port 8000 is exposed from the backend container

3. **Changes to orchestrator code not reflected**:
   - Restart the backend service to pick up changes
   - Check that file permissions allow the container to read the files

4. **Missing environment variables**:
   - Make sure all required environment variables are defined in docker-compose.yml
   - Check that .env file is properly loaded

## Deployment Considerations

For production deployment, consider:

1. Using a multi-stage build for smaller image sizes
2. Setting ENABLE_MOCK=false to use real LLM services
3. Configuring proper API keys for LLM providers
4. Enabling authentication with ENABLE_AUTH=true
5. Using a container orchestrator like Kubernetes for scalability
# Docker Orchestrator Integration

This document provides technical details on how the LLM orchestration system is integrated with Docker, enabling containerized development and deployment.

## Overview

The UltrAI orchestration system can run fully within Docker containers, providing a consistent environment for development and deployment. This approach ensures that all team members can work with the same configuration regardless of their local setup, and simplifies deployment to production environments.

## Architecture

The Docker-based orchestration system consists of the following components:

```
┌───────────────────────────────────────┐
│ Docker Environment                    │
│                                       │
│  ┌─────────────────┐  ┌─────────────┐ │
│  │  Backend        │  │  Redis      │ │
│  │  Container      │  │  Container  │ │
│  │                 │  │             │ │
│  │  - FastAPI      │◄─┼─────────────┘ │
│  │  - Orchestrator │  │               │
│  │  - LLM Adapters │  │               │
│  └────────┬────────┘  │               │
│           │           │               │
│  ┌────────▼────────┐  │               │
│  │  Worker         │  │               │
│  │  Container      │  │               │
│  │  (Optional)     │  │               │
│  │                 │  │               │
│  └─────────────────┘  │               │
│                       │               │
└───────────────────────┴───────────────┘
```

## Component Descriptions

### Backend Container

The backend container runs the FastAPI application along with the orchestration system. It:

- Handles API requests
- Manages LLM interactions through adapters
- Executes the orchestration logic
- Processes analysis modules

### Redis Container

Redis provides:

- Caching for LLM responses
- Message queuing for asynchronous tasks
- State management for multi-step orchestration

### Worker Container (Optional)

The worker container can handle background tasks such as:

- Long-running analysis processes
- Batch processing of multiple prompts
- Scheduled tasks and retries

## Configuration

### Environment Variables

The orchestration system in Docker is configured through environment variables defined in:

- `.env` file (for local development)
- `docker-compose.yml` file (for service configuration)
- Environment-specific `.env.{environment}` files (for different deployments)

Key environment variables include:

| Variable                        | Purpose                           | Example Value |
| ------------------------------- | --------------------------------- | ------------- |
| `USE_MOCK`                      | Enable mock mode for testing      | `true`        |
| `OPENAI_API_KEY`                | API key for OpenAI                | `sk-...`      |
| `ANTHROPIC_API_KEY`             | API key for Anthropic             | `sk-ant-...`  |
| `ORCHESTRATOR_ENABLE`           | Enable orchestrator functionality | `true`        |
| `ORCHESTRATOR_DEFAULT_ANALYSIS` | Default analysis type             | `comparative` |

For a full list of environment variables, see the Environment Variables Reference in the .aicheck directory.

### Volume Mappings

The Docker Compose configuration maps local directories to container paths to enable development:

| Local Path  | Container Path | Purpose                  |
| ----------- | -------------- | ------------------------ |
| `./backend` | `/app/backend` | Backend API code         |
| `./src`     | `/app/src`     | Orchestrator source code |
| `./scripts` | `/app/scripts` | Utility scripts          |
| `./logs`    | `/app/logs`    | Log storage              |
| `./data`    | `/app/data`    | Data files               |

## Usage

### Starting the Docker Environment

To start the environment with orchestrator support:

```bash
docker compose up -d backend
```

For development with live code reload:

```bash
docker compose up backend
```

### Running the Orchestrator CLI

To access the CLI interface within Docker:

```bash
docker compose exec backend python -m src.cli.menu_ultra
```

### Running Tests

To test the orchestrator in Docker:

```bash
docker compose exec backend python -m src.tests.test_orchestrator
```

## Development Workflow

1. Start the Docker environment
2. Make changes to the orchestrator code (in the `src` directory)
3. The changes are immediately available in the container due to volume mapping
4. Test changes using the CLI or API endpoints
5. Run tests to verify functionality

## Troubleshooting

### Common Issues

1. **ImportError for orchestrator modules**

   - Ensure the source code is properly mounted
   - Check the `PYTHONPATH` environment variable in the container

2. **API Authentication Failures**

   - Verify that API keys are correctly set in environment variables
   - Check if mock mode is enabled when keys are not available

3. **Container Startup Failures**
   - Check Docker logs: `docker compose logs backend`
   - Verify dependencies are installed
   - Check for port conflicts

### Debugging

For more detailed logs:

```bash
# Set higher log level
docker compose exec backend bash -c "export LOG_LEVEL=debug && python -m src.cli.menu_ultra"

# Check log files
docker compose exec backend cat /app/logs/orchestrator.log
```

## Security Considerations

1. **API Keys**

   - Never commit API keys to the repository
   - Always use environment variables for sensitive data
   - Consider using Docker secrets for production deployments

2. **Network Security**

   - The Docker network is isolated by default
   - Expose only necessary ports to the host machine
   - Consider using a VPN for remote development

3. **Data Persistence**
   - Be cautious with persisted volumes containing sensitive data
   - Consider encryption for production data volumes

## Deployment

For production deployment:

1. Use a multi-stage Dockerfile to create smaller images
2. Consider using Docker Swarm or Kubernetes for orchestration
3. Implement proper monitoring and logging
4. Set up automatic scaling based on load
5. Configure proper backup for persistent data

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Redis Docker Documentation](https://hub.docker.com/_/redis)
  EOL < /dev/null

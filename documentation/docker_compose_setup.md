# Docker Compose Setup for Ultra

This document provides comprehensive information about the Docker Compose setup for Ultra development.

## Overview

The Docker Compose configuration standardizes development environments by containerizing all required services:

- **Backend**: Ultra API service built on FastAPI
- **PostgreSQL**: Database for storing application data
- **Redis**: Used for caching and message brokering
- **Frontend**: React application (optional)

## Prerequisites

- Docker Engine (20.10.0+)
- Docker Compose (V2)
- Git
- A copy of the Ultra codebase

## Installation

1. Clone the Ultra repository (if you haven't already)

   ```bash
   git clone https://github.com/yourusername/Ultra.git
   cd Ultra
   ```

2. Create environment file

   ```bash
   cp env.example .env
   ```

3. Edit `.env` with your specific configuration

   - Update API keys
   - Set passwords for PostgreSQL and Redis
   - Configure other settings as needed

4. Build and start the containers
   ```bash
   docker-compose up -d
   ```

## Environment Variables

Key variables in `.env` that affect the Docker Compose setup:

| Variable               | Description                                 | Default           |
| ---------------------- | ------------------------------------------- | ----------------- |
| `BUILD_TARGET`         | Build stage to use (development/production) | development       |
| `TAG`                  | Docker image tag                            | latest            |
| `COMPOSE_PROJECT_NAME` | Project name prefix for containers          | ultra             |
| `RESTART_POLICY`       | Container restart policy                    | unless-stopped    |
| `DB_HOST`              | PostgreSQL hostname                         | postgres          |
| `DB_PORT`              | PostgreSQL port                             | 5432              |
| `DB_USER`              | PostgreSQL username                         | postgres          |
| `DB_PASSWORD`          | PostgreSQL password                         | postgres_password |
| `DB_NAME`              | PostgreSQL database name                    | ultra             |
| `REDIS_HOST`           | Redis hostname                              | redis             |
| `REDIS_PORT`           | Redis port                                  | 6379              |
| `REDIS_PASSWORD`       | Redis password                              | redis_password    |
| `FRONTEND_PORT`        | Frontend service port                       | 3009              |

## Service Details

### Backend Service

- Built from the project's Dockerfile
- Uses multi-stage builds for development vs. production
- Automatically reloads code when changes are detected
- Connects to PostgreSQL and Redis using their service names
- Exposes port 8000 for API access

### PostgreSQL Service

- Uses official PostgreSQL 15 image
- Persists data in a named volume
- Initialized with custom scripts that create the Ultra schema
- Runs with appropriate performance settings for development
- Exposes port 5432 for direct database access

### Redis Service

- Uses official Redis 7 image
- Persists data in a named volume
- Configured with password authentication
- Exposes port 6379 for direct Redis access

### Frontend Service (Optional)

- Uses Node.js for building and serving the React app
- Auto-reloads when code changes are detected
- Configured to connect to the backend service
- Exposes port 3009 for web access

## Networks and Volumes

- **Networks**: All services run on a dedicated `ultra-network` for isolated communication
- **Volumes**:
  - `postgres-data`: Persistent storage for PostgreSQL
  - `redis-data`: Persistent storage for Redis
  - Source code directories are mounted as volumes for development

## CI/CD Integration

A separate `docker-compose.ci.yml` file is provided for CI/CD environments with:

- Fixed image tags
- Simplified configuration
- Standardized environment variables
- No volume persistence
- Pre-configured test settings

## Performance Considerations

The Docker Compose setup is optimized for development with:

- Memory limits appropriate for local development
- CPU constraints to prevent resource starvation
- Swap configured to handle memory spikes
- Appropriate PostgreSQL configuration for development workloads

## Troubleshooting

### Common Issues

1. **Container fails to start**

   - Check logs: `docker-compose logs backend`
   - Verify environment variables in `.env`
   - Ensure ports are not already in use

2. **Database connection fails**

   - Verify PostgreSQL container is running: `docker-compose ps postgres`
   - Check database initialization: `docker-compose logs postgres`
   - Ensure DB\_\* environment variables are correctly set

3. **Redis connection fails**

   - Verify Redis container is running: `docker-compose ps redis`
   - Check Redis logs: `docker-compose logs redis`
   - Ensure REDIS\_\* environment variables are correctly set

4. **Changes not reflected**
   - Verify volumes are mounted correctly
   - Restart the service: `docker-compose restart backend`
   - Rebuild if necessary: `docker-compose build backend`

### Debugging Commands

```bash
# Check container status
docker-compose ps

# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend

# Enter a container shell
docker-compose exec backend bash

# Check network connectivity
docker-compose exec backend ping postgres

# View container resource usage
docker stats

# Restart all services
docker-compose restart
```

## Extending the Setup

### Adding New Services

To add a new service:

1. Add the service definition to `docker-compose.yml`
2. Update `.env.example` with new environment variables
3. Ensure proper network configuration
4. Update documentation

### Custom Configuration

For development-specific customizations, create a `docker-compose.override.yml` file with your changes.

## Maintenance

- Regularly update base images: `docker-compose pull`
- Rebuild containers to incorporate dependency changes: `docker-compose build`
- Clean up unused resources: `docker system prune`

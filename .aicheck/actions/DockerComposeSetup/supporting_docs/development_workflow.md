# Development Workflow with Docker Compose

This document outlines the development workflow when using Docker Compose with the Ultra project.

## Overview

Docker Compose provides a standardized development environment where all dependencies (PostgreSQL, Redis) are containerized alongside the Ultra backend and frontend services. This ensures that all developers have an identical setup regardless of their local operating system or environment.

## Initial Setup

### Prerequisites

- Docker Engine (20.10.0+)
- Docker Compose (v2.0.0+)
- Git

### First-time Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Ultra.git
   cd Ultra
   ```

2. Create your environment file:
   ```bash
   cp env.example .env
   ```

3. Edit the `.env` file to set any required API keys or configuration options.

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

5. Initialize the database (if needed):
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Daily Development

### Starting the Environment

Start all services in detached mode:
```bash
docker-compose up -d
```

### Viewing Logs

View logs for all services:
```bash
docker-compose logs -f
```

View logs for a specific service:
```bash
docker-compose logs -f backend
```

### Code Changes

1. Make changes to your code in your local editor
2. The backend service uses volume mounts and auto-reload, so changes are immediately reflected
3. For the frontend, changes are also automatically detected and rebuilt

### Running Tests

Run tests in the container:
```bash
docker-compose exec backend pytest
```

Run specific tests:
```bash
docker-compose exec backend pytest backend/tests/test_specific.py -v
```

### Database Operations

Access the PostgreSQL CLI:
```bash
docker-compose exec postgres psql -U postgres -d ultra
```

Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

Create a new migration:
```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Working with Redis

Access the Redis CLI:
```bash
docker-compose exec redis redis-cli -a $(grep REDIS_PASSWORD .env | cut -d '=' -f2)
```

Clear Redis cache:
```bash
docker-compose exec redis redis-cli -a $(grep REDIS_PASSWORD .env | cut -d '=' -f2) FLUSHALL
```

### Adding Dependencies

When adding new Python dependencies:

1. Update `requirements.txt`
2. Rebuild the backend container:
   ```bash
   docker-compose build backend
   ```
3. Restart the backend service:
   ```bash
   docker-compose restart backend
   ```

For frontend dependencies:

1. Update `package.json`
2. Rebuild the frontend container:
   ```bash
   docker-compose build frontend
   ```
3. Restart the frontend service:
   ```bash
   docker-compose restart frontend
   ```

## Stopping the Environment

Stop all services but preserve data:
```bash
docker-compose down
```

Stop all services and remove volumes (data will be lost):
```bash
docker-compose down -v
```

## Common Tasks

### Rebuilding Services

Rebuild a specific service:
```bash
docker-compose build backend
```

Rebuild all services:
```bash
docker-compose build
```

### Restarting Services

Restart a specific service:
```bash
docker-compose restart backend
```

Restart all services:
```bash
docker-compose restart
```

### Executing Commands

Run a one-off command in a service:
```bash
docker-compose exec backend python -c "import sys; print(sys.version)"
```

Start a shell in a container:
```bash
docker-compose exec backend bash
```

### Monitoring

View container status:
```bash
docker-compose ps
```

View resource usage:
```bash
docker stats
```

## Troubleshooting

### Service Won't Start

1. Check the logs:
   ```bash
   docker-compose logs service_name
   ```

2. Verify environment variables:
   ```bash
   docker-compose config
   ```

3. Check for port conflicts:
   ```bash
   netstat -tuln
   ```

### Database Connection Issues

1. Verify the database is running:
   ```bash
   docker-compose ps postgres
   ```

2. Check database logs:
   ```bash
   docker-compose logs postgres
   ```

3. Verify connection settings in `.env`

### Redis Connection Issues

1. Verify Redis is running:
   ```bash
   docker-compose ps redis
   ```

2. Check Redis logs:
   ```bash
   docker-compose logs redis
   ```

3. Verify connection settings in `.env`

### Changes Not Reflected

1. Ensure the service is using volume mounts for code
2. Verify the auto-reload setting is enabled
3. Restart the service:
   ```bash
   docker-compose restart service_name
   ```

## Best Practices

1. **Use named volumes for data persistence**
   - PostgreSQL and Redis data should be stored in named volumes
   - This ensures data persists across container restarts

2. **Use consistent environment variables**
   - Keep your `.env` file up to date
   - Use the same variable names across all environments

3. **Isolate services**
   - Use separate networks for isolating components
   - Expose only necessary ports

4. **Keep Docker images lean**
   - Use multi-stage builds
   - Avoid installing unnecessary packages

5. **Use health checks**
   - Implement health checks for each service
   - Services should wait for dependencies to be healthy before starting

6. **Regular maintenance**
   - Update base images
   - Prune unused volumes and networks
   - Clean up old containers
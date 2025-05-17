# Deployment Troubleshooting Guide

This guide addresses common issues that may occur during the deployment of Ultra AI and provides solutions to resolve them.

## Table of Contents

1. [General Troubleshooting Approach](#general-troubleshooting-approach)
2. [Docker Deployment Issues](#docker-deployment-issues)
3. [Database Connectivity Issues](#database-connectivity-issues)
4. [Redis Connectivity Issues](#redis-connectivity-issues)
5. [LLM Provider Issues](#llm-provider-issues)
6. [Performance Issues](#performance-issues)
7. [Security and Authentication Issues](#security-and-authentication-issues)
8. [Rollback Problems](#rollback-problems)

## General Troubleshooting Approach

When troubleshooting deployment issues, follow these general steps:

1. **Check Logs**: Always start by examining the relevant logs:

   ```bash
   docker-compose logs --tail=100           # View the most recent logs
   docker-compose logs --tail=100 backend   # View logs for a specific service
   docker-compose logs --tail=100 --follow  # Follow logs in real time
   ```

2. **Check Service Status**:

   ```bash
   docker-compose ps           # View the status of all services
   docker stats                # Monitor resource usage
   ```

3. **Check API Health**:

   ```bash
   curl http://localhost:8000/health                  # Basic health check
   curl http://localhost:8000/health?detail=true      # Detailed health check
   curl http://localhost:8000/health/database         # Database health
   curl http://localhost:8000/health/llm/providers    # LLM provider health
   ```

4. **Isolate the Issue**: Determine if the issue is:
   - Environment-specific (works in dev but not prod)
   - Service-specific (database works but Redis fails)
   - Timing-related (works sometimes)
   - Load-related (fails under high traffic)

## Docker Deployment Issues

### Services Fail to Start

**Symptoms**: Containers exit immediately or enter a restart loop.

**Solutions**:

1. Check container logs for specific error messages:

   ```bash
   docker-compose logs backend
   ```

2. Verify environment variables:

   ```bash
   docker-compose config   # Shows resolved configuration
   ```

3. Check for port conflicts:

   ```bash
   sudo lsof -i :8000   # Check if port 8000 is already in use
   sudo lsof -i :5432   # Check if port 5432 (PostgreSQL) is in use
   ```

4. Try starting services one by one:
   ```bash
   docker-compose up -d postgres
   docker-compose up -d redis
   docker-compose up -d backend
   ```

### Image Build Failures

**Symptoms**: Docker build fails with errors.

**Solutions**:

1. Check Docker build logs for specific errors.

2. Try cleaning Docker cache:

   ```bash
   docker builder prune -f
   ```

3. Ensure dependencies are available:

   ```bash
   docker-compose build --pull   # Force pull latest base images
   ```

4. Check disk space:
   ```bash
   df -h   # Make sure you have enough disk space
   ```

## Database Connectivity Issues

### Database Connection Fails

**Symptoms**: Backend service cannot connect to the database.

**Solutions**:

1. Check database container is running:

   ```bash
   docker-compose ps postgres
   ```

2. Verify database credentials match in the environment file and Docker Compose file.

3. Check if PostgreSQL is accepting connections:

   ```bash
   docker-compose exec postgres pg_isready -U ultra
   ```

4. Check PostgreSQL logs:

   ```bash
   docker-compose logs postgres
   ```

5. Try connecting manually:
   ```bash
   docker-compose exec postgres psql -U ultra -d ultra_dev
   ```

### Database Migration Issues

**Symptoms**: Application reports missing tables or columns.

**Solutions**:

1. Run migrations manually:

   ```bash
   docker-compose exec backend alembic upgrade head
   ```

2. Check migration status:

   ```bash
   docker-compose exec backend alembic current
   ```

3. If migrations are corrupted, you may need to reset:
   ```bash
   docker-compose exec backend alembic downgrade base
   docker-compose exec backend alembic upgrade head
   ```

## Redis Connectivity Issues

### Redis Connection Fails

**Symptoms**: Cache operations fail, backend logs show Redis connection errors.

**Solutions**:

1. Check Redis container is running:

   ```bash
   docker-compose ps redis
   ```

2. Verify Redis password is correct in environment variables.

3. Check Redis is accepting connections:

   ```bash
   docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping
   ```

4. Check Redis memory usage:
   ```bash
   docker-compose exec redis redis-cli -a $REDIS_PASSWORD info memory
   ```

### Redis Performance Issues

**Symptoms**: Redis operations are slow or timing out.

**Solutions**:

1. Check Redis memory usage and configuration:

   ```bash
   docker-compose exec redis redis-cli -a $REDIS_PASSWORD info
   ```

2. Consider clearing Redis cache:

   ```bash
   docker-compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHALL
   ```

3. Check for large keys that might be causing issues:
   ```bash
   docker-compose exec redis redis-cli -a $REDIS_PASSWORD --bigkeys
   ```

## LLM Provider Issues

### LLM Providers Not Available

**Symptoms**: Health check shows LLM providers as unavailable, API requests fail.

**Solutions**:

1. Check API keys are correctly set in environment variables.

2. Verify network connectivity to external APIs:

   ```bash
   docker-compose exec backend curl -I https://api.openai.com/v1
   docker-compose exec backend curl -I https://api.anthropic.com
   ```

3. Check if API keys have sufficient quota or if rate limits are being exceeded.

4. Enable mock mode temporarily:
   ```bash
   # Edit .env file
   USE_MOCK=true
   ```

### Docker Model Runner Issues

**Symptoms**: Local models are not available, model-runner container fails.

**Solutions**:

1. Check model-runner container is running:

   ```bash
   docker-compose ps model-runner
   ```

2. Check model-runner logs:

   ```bash
   docker-compose logs model-runner
   ```

3. Verify models are correctly downloaded:

   ```bash
   docker-compose exec model-runner docker model list
   ```

4. Check resource allocation (GPU access, memory limits).

## Performance Issues

### High Latency

**Symptoms**: API requests take longer than expected to complete.

**Solutions**:

1. Check system resource usage:

   ```bash
   docker stats
   ```

2. Check if database queries are slow:

   ```bash
   # Check PostgreSQL slow query log
   docker-compose exec postgres cat /var/log/postgresql/postgresql-slow.log
   ```

3. Check Redis performance:

   ```bash
   docker-compose exec redis redis-cli -a $REDIS_PASSWORD --latency
   ```

4. Investigate if LLM API calls are the bottleneck:
   ```bash
   # Check response times in application logs
   docker-compose logs backend | grep "response time"
   ```

### Memory Issues

**Symptoms**: Containers crash with OOM (Out of Memory) errors.

**Solutions**:

1. Increase memory limits in Docker Compose file.

2. Check for memory leaks in the application.

3. Enable more aggressive garbage collection:

   ```bash
   # For Python backend
   export PYTHONMALLOC=debug
   ```

4. Consider adding more swap space to the host system.

## Security and Authentication Issues

### JWT Authentication Fails

**Symptoms**: Authentication endpoints return 401 or 403 errors.

**Solutions**:

1. Check JWT_SECRET is set correctly and consistently.

2. Verify token expiration settings are appropriate.

3. Check if clocks are synchronized between services.

4. Look for CORS issues if browser-based clients are failing.

### API Key Issues

**Symptoms**: API requests with keys fail with authentication errors.

**Solutions**:

1. Verify API keys are properly formatted and not expired.

2. Check if rate limits are being exceeded.

3. Verify the API key validation logic in the application.

## Rollback Problems

### Automatic Rollback Fails

**Symptoms**: Rollback script completes but application is not functioning correctly.

**Solutions**:

1. Check rollback logs:

   ```bash
   cat logs/rollback_$(date +%Y%m%d).log
   ```

2. Verify backup archive was extracted correctly:

   ```bash
   ls -la rollbacks/
   ```

3. Try a manual rollback:

   ```bash
   # Stop all containers
   docker-compose down

   # Restore from backup
   tar -xzf backups/production/backup-20250511-120345.tar.gz -C ./

   # Start services
   docker-compose up -d
   ```

### No Suitable Backup Available

**Symptoms**: No recent backups found or all backups are corrupted.

**Solutions**:

1. Check the backups directory:

   ```bash
   ls -la backups/production/
   ```

2. If no suitable backup exists, perform a fresh deployment:

   ```bash
   git checkout main
   ./scripts/deploy-mvp.sh --environment production
   ```

3. Restore database from the most recent database backup if available:
   ```bash
   cat backups/database/ultra_dev_latest.sql | docker-compose exec -T postgres psql -U ultra ultra_dev
   ```

## Common Error Messages and Solutions

| Error Message                      | Possible Cause                                              | Solution                                                          |
| ---------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------- |
| `Connection refused to PostgreSQL` | Database container not running or wrong connection settings | Check PostgreSQL container status and connection configuration    |
| `Redis connection error`           | Redis container not running or password incorrect           | Verify Redis container status and credentials                     |
| `API key invalid`                  | LLM provider API key is incorrect or expired                | Check and update API keys in environment file                     |
| `No space left on device`          | Docker host has run out of disk space                       | Clean up unused Docker images, volumes, and containers            |
| `Permission denied`                | File permissions issue                                      | Check file ownership and permissions in mounted volumes           |
| `Out of memory`                    | Container exceeding memory limits                           | Increase memory allocation in Docker Compose file                 |
| `Circuit breaker open`             | Too many failures have occurred to an external service      | Check external service health and review circuit breaker settings |

## Additional Troubleshooting Resources

- Docker troubleshooting: [Docker Documentation](https://docs.docker.com/engine/troubleshoot/)
- PostgreSQL troubleshooting: [PostgreSQL Wiki](https://wiki.postgresql.org/wiki/Main_Page)
- Redis troubleshooting: [Redis Documentation](https://redis.io/docs/latest/operate/troubleshooting/)
- FastAPI troubleshooting: [FastAPI Documentation](https://fastapi.tiangolo.com/tutorial/debugging/)

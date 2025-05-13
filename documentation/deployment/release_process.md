# Ultra AI Release Process

This document outlines the standard release process for Ultra AI, covering development, staging, and production deployments.

## Table of Contents

1. [Release Workflow](#release-workflow)
2. [Pre-release Checklist](#pre-release-checklist)
3. [Deployment Instructions](#deployment-instructions)
4. [Verification Procedures](#verification-procedures)
5. [Rollback Procedures](#rollback-procedures)
6. [Maintenance Tasks](#maintenance-tasks)

## Release Workflow

Ultra AI follows a structured release workflow to ensure consistent, reliable deployments:

```
Feature Development → Testing → Staging Deployment → Production Deployment
```

### Development Cycle

1. **Feature Branch**: Developers work in feature branches following the naming convention `feature/[feature-name]`.
2. **Pull Request**: When a feature is complete, a PR is created targeting the `main` branch.
3. **Code Review**: At least one other developer must review and approve the PR.
4. **CI Tests**: All automated tests must pass before merging.
5. **Merge**: After approval and passing tests, the PR is merged into `main`.

### Release Cycle

1. **Release Planning**: Features to be included in a release are identified and tracked.
2. **Release Branch**: A branch named `release/v[version]` is created from `main`.
3. **Release Testing**: Comprehensive testing is performed on the release branch.
4. **Staging Deployment**: The release is deployed to staging for final validation.
5. **Production Deployment**: After successful staging validation, the release is deployed to production.
6. **Tagging**: After successful deployment, a tag is created in the repository with the version number.

## Pre-release Checklist

Before initiating a deployment, ensure the following items are checked:

### Code Quality

- [ ] All automated tests are passing
- [ ] Code has been reviewed and approved
- [ ] No known critical bugs remain unresolved
- [ ] Documentation has been updated

### Configuration

- [ ] Environment variables are properly set for the target environment
- [ ] Database migrations are prepared if needed
- [ ] API keys for LLM providers are valid and have sufficient quota
- [ ] Feature flags are configured appropriately

### Infrastructure

- [ ] Sufficient resources are available (disk space, memory, etc.)
- [ ] Backups of the current state have been created
- [ ] Monitoring systems are functional
- [ ] Database is healthy and has sufficient capacity

### Security

- [ ] Security scan has been performed on dependencies
- [ ] API keys and secrets are properly secured
- [ ] Authentication and authorization systems are tested
- [ ] Rate limiting and other protection mechanisms are enabled

## Deployment Instructions

### Preparing for Deployment

1. Create a release branch if not already done:
   ```bash
   git checkout main
   git pull
   git checkout -b release/v1.2.3
   ```

2. Ensure the correct environment configuration:
   - Check `.env.development` for development deployments
   - Check `.env.production` for production deployments
   - Verify all required environment variables are set

3. Update the version number:
   - In `package.json` (if applicable)
   - In environment file

### Executing Deployment

The deployment process is automated through the `deploy-mvp.sh` script:

**Development Deployment:**

```bash
./scripts/deploy-mvp.sh --environment development
```

**Production Deployment:**

```bash
./scripts/deploy-mvp.sh --environment production --tag v1.2.3
```

**Additional Options:**

- `--skip-tests`: Skip running tests (not recommended for production)
- `--skip-build`: Skip building Docker images
- `--compose [file]`: Specify a custom Docker Compose file
- `--registry [url]`: Specify a Docker registry for image push

### Post-Deployment Steps

1. Verify the deployment (see [Verification Procedures](#verification-procedures))
2. Create a git tag for the release:
   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin v1.2.3
   ```
3. Update the deployment documentation with any issues encountered

## Verification Procedures

After deployment, it's critical to verify that the system is functioning correctly:

### Automated Verification

Run the verification script to check all critical systems:

```bash
./scripts/verify-deployment.sh --environment [environment]
```

This script runs a suite of tests to ensure:
- Health endpoints are responding
- Database connectivity is working
- Redis cache is available
- LLM providers are accessible
- API endpoints are functioning correctly

### Manual Verification

For critical releases, perform additional manual verification:

1. Test user authentication flow (if enabled)
2. Submit a test prompt and verify the response
3. Test file upload functionality (if applicable)
4. Check the UI for any visual issues (for frontend deployments)
5. Verify metrics and monitoring are capturing data correctly

### Performance Verification

For production deployments, verify performance:

1. Check response times for critical API endpoints
2. Monitor server resource usage (CPU, memory, disk)
3. Verify database query performance
4. Check LLM request latency is within acceptable ranges

## Rollback Procedures

If issues are detected after deployment, the system can be rolled back to a previous state:

### Automated Rollback

Use the rollback script to restore from the most recent backup:

```bash
./scripts/rollback-mvp.sh --environment [environment]
```

To roll back to a specific backup:

```bash
./scripts/rollback-mvp.sh --environment [environment] --backup [backup-id]
```

To list available backups:

```bash
./scripts/rollback-mvp.sh --environment [environment]
```

### Manual Rollback

If the automated rollback fails, follow these manual steps:

1. Stop the current services:
   ```bash
   docker-compose down
   ```

2. Restore from a backup:
   ```bash
   # Locate the latest backup
   ls -l backups/[environment]/

   # Extract the backup
   mkdir -p rollback
   tar -xzf backups/[environment]/[backup-file] -C rollback/

   # Copy files back
   cp -r rollback/* ./
   ```

3. Restart services:
   ```bash
   docker-compose up -d
   ```

4. Verify the rollback was successful:
   ```bash
   ./scripts/verify-deployment.sh --environment [environment]
   ```

## Maintenance Tasks

### Database Maintenance

Regular database maintenance tasks:

1. **Backups**: Database is automatically backed up during deployment, but additional backups can be created:
   ```bash
   docker-compose exec postgres pg_dump -U ultra ultra_dev > backups/database/ultra_dev_$(date +%Y%m%d).sql
   ```

2. **Vacuum**: Run vacuum to reclaim space and improve performance:
   ```bash
   docker-compose exec postgres psql -U ultra -d ultra_dev -c "VACUUM ANALYZE;"
   ```

### Log Management

1. **Rotating Logs**: Logs are automatically rotated, but check disk space regularly:
   ```bash
   docker-compose exec backend df -h /app/logs
   ```

2. **Archiving Logs**: Archive old logs if needed:
   ```bash
   tar -czf logs/archive/logs_$(date +%Y%m%d).tar.gz logs/*.log
   ```

### Monitoring

1. **Check System Health**: View system health and metrics:
   ```bash
   curl http://localhost:8000/health?detail=true
   ```

2. **View Container Status**:
   ```bash
   docker-compose ps
   docker stats
   ```

### Cache Management

1. **Clear Cache**: If needed, clear the Redis cache:
   ```bash
   docker-compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHALL
   ```

2. **Check Cache Size**:
   ```bash
   docker-compose exec redis redis-cli -a $REDIS_PASSWORD info | grep used_memory_human
   ```

## Release Calendar

Ultra AI follows this release schedule:

- **Development Deployments**: As needed for feature testing
- **Staging Deployments**: Weekly (typically Tuesdays)
- **Production Deployments**: Bi-weekly (typically every other Thursday)
- **Emergency Fixes**: As needed, following abbreviated but complete testing
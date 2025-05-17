# Ultra MVP - Production Deployment Runbook

## Pre-Deployment Checklist

### 1. Environment Preparation
- [ ] Backup current production (if exists)
- [ ] Verify Docker images built: `docker images | grep ultra`
- [ ] Check disk space: `df -h` (need 10GB free)
- [ ] Verify network connectivity to:
  - [ ] PostgreSQL server
  - [ ] Redis server
  - [ ] LLM API endpoints

### 2. Configuration Files
- [ ] Copy `.env.production` to deployment server
- [ ] Verify all required variables set
- [ ] Validate JWT secrets are secure (32+ chars)
- [ ] Confirm API keys are production keys

### 3. Database Preparation
- [ ] Create production database if not exists
- [ ] Run database migrations:
  ```bash
  alembic upgrade head
  ```
- [ ] Verify migrations successful
- [ ] Create database backup

### 4. Team Notifications
- [ ] Notify development team of deployment window
- [ ] Alert support team of upcoming changes
- [ ] Update status page with maintenance window

## Deployment Steps

### Step 1: Stop Current Services (if applicable)
```bash
# Stop existing containers
docker-compose down

# Wait for graceful shutdown
sleep 10
```

### Step 2: Pull Latest Images
```bash
# Pull the latest images
docker pull ultraai/backend:latest
docker pull ultraai/frontend:latest
```

### Step 3: Update Configuration
```bash
# Load production environment
export $(cat .env.production | grep -v '^#' | xargs)

# Verify critical variables
echo "ENABLE_AUTH: $ENABLE_AUTH"  # Should be "true"
echo "USE_MOCK: $USE_MOCK"        # Should be "false"
```

### Step 4: Start Services
```bash
# Start infrastructure services first
docker-compose up -d postgres redis

# Wait for services to be healthy
while ! docker-compose ps | grep -q "healthy"; do
  echo "Waiting for services..."
  sleep 5
done

# Start application services
docker-compose up -d backend frontend
```

### Step 5: Run Health Checks
```bash
# Check backend health
curl http://localhost:8085/api/health

# Expected response:
# {"status":"healthy","services":{...}}
```

### Step 6: Verify Authentication
```bash
# Test authentication endpoint
curl -X POST http://localhost:8085/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'

# Should return 401 or successful auth
```

### Step 7: Test LLM Connectivity
```bash
# Test LLM endpoint
curl -X POST http://localhost:8085/api/v1/chat/completions \
  -H "Authorization: Bearer $TEST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"model":"gpt-4o"}'
```

### Step 8: Monitor Logs
```bash
# Watch backend logs
docker-compose logs -f backend

# Check for any ERROR level messages
# Confirm "Application startup complete"
```

## Post-Deployment Verification

### Immediate Checks (First 15 minutes)
- [ ] Health endpoint responding
- [ ] No ERROR logs in backend
- [ ] Authentication working
- [ ] LLM requests successful
- [ ] Database connections stable
- [ ] Redis operations working

### First Hour Checks
- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify memory usage stable
- [ ] Confirm no connection leaks
- [ ] Review security logs

### First Day Checks
- [ ] Analyze usage patterns
- [ ] Review performance metrics
- [ ] Check error tracking system
- [ ] Verify backup completed
- [ ] Update documentation

## Rollback Procedure

### If Critical Issues Occur:

#### 1. Immediate Rollback
```bash
# Stop current deployment
docker-compose down

# Restore previous version
docker-compose up -d --file docker-compose.backup.yml

# Clear Redis cache
docker exec ultra-redis redis-cli FLUSHALL
```

#### 2. Database Rollback
```bash
# If schema changed
alembic downgrade -1

# If data corrupted
psql $DATABASE_URL < backup.sql
```

#### 3. Communication
- [ ] Update status page
- [ ] Notify stakeholders
- [ ] Create incident report
- [ ] Schedule post-mortem

## Monitoring Commands

### Container Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats
```

### Application Logs
```bash
# All logs
docker-compose logs

# Specific service
docker-compose logs backend -f --tail=100
```

### Database Connections
```bash
docker exec ultra-postgres psql -U $POSTGRES_USER -c "SELECT count(*) FROM pg_stat_activity;"
```

### Redis Status
```bash
docker exec ultra-redis redis-cli INFO
```

## Troubleshooting

### Issue: Services Won't Start
```bash
# Check port conflicts
netstat -tulpn | grep -E '(8085|5432|6379)'

# Check Docker daemon
docker version

# Check compose file
docker-compose config
```

### Issue: Database Connection Failed
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check firewall
telnet $DB_HOST 5432
```

### Issue: Redis Connection Failed
```bash
# Test connection
redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD ping
```

### Issue: High Memory Usage
```bash
# Check container limits
docker inspect backend | grep -i memory

# Restart with limits
docker-compose up -d --memory="2g" backend
```

## Emergency Contacts

- **DevOps Lead**: [Name] - [Phone] - [Email]
- **Database Admin**: [Name] - [Phone] - [Email]
- **Security Team**: [Name] - [Phone] - [Email]
- **On-Call Engineer**: [Phone]

## Success Criteria

Deployment is successful when:
- [ ] All containers running
- [ ] Health checks passing
- [ ] No critical errors in logs
- [ ] Authentication functional
- [ ] LLM requests working
- [ ] Performance metrics normal
- [ ] Monitoring alerts configured

---

*Version: 1.0*  
*Last Updated: May 16, 2025*  
*Next Review: June 16, 2025*
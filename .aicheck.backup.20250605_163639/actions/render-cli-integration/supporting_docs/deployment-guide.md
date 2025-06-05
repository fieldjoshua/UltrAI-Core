# UltraAI Render Deployment Guide

## Overview

This guide provides step-by-step procedures for deploying UltraAI to production using Render CLI integration, with automated verification to prevent deployment issues.

## Prerequisites

- Git repository up to date
- Render account access
- Render CLI installed and authenticated
- Production URL: https://ultrai-core-4lut.onrender.com

## Quick Deployment

### 1. Automated Deployment (Recommended)

```bash
# Run the automated deployment script
./scripts/deploy-render.sh
```

This script will:
- Check git status and branch
- Guide you through manual deployment trigger
- Verify deployment success
- Test sophisticated orchestrator endpoints

### 2. Manual Verification

```bash
# Verify production is running sophisticated code
./scripts/verify-production.sh
```

## Detailed Procedures

### Pre-Deployment Checklist

1. **Code Verification**
   ```bash
   git status  # Should be clean
   git branch  # Should be on main
   git log --oneline -5  # Check recent commits
   ```

2. **Local Testing**
   ```bash
   # Test sophisticated orchestrator locally
   python -c "from src.core.ultra_pattern_orchestrator import PatternOrchestrator; print('✅ Orchestrator imports OK')"
   ```

3. **Environment Variables**
   - Verify API keys are set in Render dashboard
   - Check production environment configuration
   - Confirm service settings match requirements

### Deployment Process

#### Method 1: Render CLI Guided (Recommended)

1. **Run Deployment Script**
   ```bash
   ./scripts/deploy-render.sh
   ```

2. **Follow Interactive Prompts**
   - Script will check git status
   - Guide you to Render dashboard
   - Wait for deployment completion
   - Automatically verify results

#### Method 2: Manual Dashboard

1. **Access Render Dashboard**
   - Go to https://dashboard.render.com
   - Navigate to ultrai-core service

2. **Trigger Deployment**
   - Click "Manual Deploy"
   - Select "Deploy latest commit"
   - Monitor build progress

3. **Verify Deployment**
   ```bash
   ./scripts/verify-production.sh
   ```

### Post-Deployment Verification

#### Critical Endpoints Test

The verification script checks these critical endpoints:

1. **Health Check**
   ```
   GET https://ultrai-core-4lut.onrender.com/health
   Expected: {"status": "ok", "services": {...}}
   ```

2. **Sophisticated Orchestrator**
   ```
   GET https://ultrai-core-4lut.onrender.com/api/orchestrator/models
   Expected: List of available LLM models
   
   GET https://ultrai-core-4lut.onrender.com/api/orchestrator/patterns  
   Expected: Array of 10 analysis patterns
   
   GET https://ultrai-core-4lut.onrender.com/api/orchestrator/feather
   Expected: 4-stage Feather orchestration endpoint
   ```

3. **API Documentation**
   ```
   GET https://ultrai-core-4lut.onrender.com/openapi.json
   Expected: Complete OpenAPI specification
   ```

#### Success Criteria

✅ **Deployment Successful If:**
- Health endpoint returns status: "ok"
- All 3 sophisticated orchestrator endpoints respond
- API documentation shows 14+ endpoints
- Response times under 5 seconds

❌ **Deployment Failed If:**
- Sophisticated endpoints return 404 Not Found
- Only /api/orchestrator/execute endpoint exists (antiquated)
- Health endpoint fails
- Critical failures in verification script

## Troubleshooting

### Issue: Antiquated Code Running

**Symptoms:**
- `/api/orchestrator/models` returns 404
- `/api/orchestrator/patterns` returns 404
- Only `/api/orchestrator/execute` exists

**Solutions:**
1. **Clear Build Cache**
   - Go to Render dashboard
   - Service Settings → Clear Build Cache
   - Trigger new deployment

2. **Check Blueprint Status**
   - Verify blueprint is disconnected (if applicable)
   - Check manual configuration matches requirements

3. **Verify Git State**
   ```bash
   git log --grep="orchestrat" -10
   # Should show orchestration integration commits
   ```

### Issue: Environment Variables

**Symptoms:**
- Service fails to start
- API key errors in logs
- Database connection issues

**Solutions:**
1. **Check Required Variables**
   - OPENAI_API_KEY
   - ANTHROPIC_API_KEY
   - GOOGLE_API_KEY
   - JWT_SECRET
   - SECRET_KEY

2. **Verify in Dashboard**
   - Service Settings → Environment Variables
   - Ensure all keys are set and not expired

### Issue: Build Failures

**Symptoms:**
- Deployment fails during build
- Missing dependencies errors
- Python version issues

**Solutions:**
1. **Check Requirements**
   ```bash
   cat requirements-production.txt
   # Verify all dependencies are listed
   ```

2. **Python Version**
   - Ensure Python 3.11+ in environment variables
   - Check runtime.txt if present

3. **Build Command**
   ```
   pip install -r requirements-production.txt
   ```

## Emergency Procedures

### Rollback to Previous Version

1. **Identify Last Working Commit**
   ```bash
   git log --oneline -10
   ```

2. **Force Deploy Previous Commit**
   - Use Render dashboard
   - Manual Deploy → Deploy specific commit
   - Select last known working commit

3. **Verify Rollback**
   ```bash
   ./scripts/verify-production.sh
   ```

### Complete Service Reset

1. **Delete and Recreate Service**
   - Backup environment variables
   - Delete service in Render dashboard
   - Create new service with same configuration

2. **Reconfigure**
   - Set environment variables
   - Configure build/start commands
   - Deploy latest code

## Monitoring and Maintenance

### Regular Health Checks

```bash
# Daily verification
./scripts/verify-production.sh

# Check service status
curl -s https://ultrai-core-4lut.onrender.com/health | jq '.'
```

### Performance Monitoring

- Monitor response times in verification script
- Check for memory/CPU issues in Render dashboard
- Watch for failed requests in logs

### Security Updates

- Regularly update dependencies
- Monitor for security advisories
- Keep API keys rotated

## Script Reference

### deploy-render.sh
- Pre-deployment git checks
- Interactive deployment guidance
- Post-deployment verification
- Error handling and reporting

### verify-production.sh
- Comprehensive endpoint testing
- Sophisticated vs antiquated code detection
- Performance monitoring
- Detailed reporting

Both scripts include:
- Colored output for clarity
- Error handling and recovery suggestions
- Detailed logging of results
- Exit codes for automation integration
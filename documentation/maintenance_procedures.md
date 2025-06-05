# UltraAI System Maintenance Procedures
*Version: 1.0*
*Last Updated: 2025-06-04*

## 📋 Table of Contents
1. [Daily Maintenance](#daily-maintenance)
2. [Weekly Maintenance](#weekly-maintenance)
3. [Deployment Procedures](#deployment-procedures)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Emergency Procedures](#emergency-procedures)
6. [Configuration Management](#configuration-management)

## 🔄 Daily Maintenance

### Morning Health Check (9:00 AM)
```bash
# 1. Check all health endpoints
curl https://ultrai-core.onrender.com/api/health
curl https://ultrai-core.onrender.com/api/health/llm
curl https://ultrai-core.onrender.com/api/health/orchestrator

# 2. Verify frontend connectivity
curl https://ultra-ai.vercel.app

# 3. Check error logs
# Access Render dashboard → ultrai-core → Logs
```

### Performance Monitoring
- Monitor response times via Render metrics
- Check Redis cache hit rates
- Review PostgreSQL query performance
- Track API usage patterns

### Quick Status Check Script
```bash
#!/bin/bash
# save as check_ultra_status.sh
echo "🔍 Checking UltraAI System Status..."
echo "=================================="
echo "Backend Health:"
curl -s https://ultrai-core.onrender.com/api/health | jq .
echo -e "\nOrchestrator Status:"
curl -s https://ultrai-core.onrender.com/api/orchestrator/patterns | jq '. | length'
echo " patterns available"
```

## 📅 Weekly Maintenance

### Monday: Security Review
- [ ] Review security headers configuration
- [ ] Check for any security alerts in logs
- [ ] Verify JWT token expiration settings
- [ ] Review CORS configuration

### Wednesday: Performance Optimization
- [ ] Analyze slow query logs
- [ ] Review Redis memory usage
- [ ] Check for memory leaks
- [ ] Optimize any identified bottlenecks

### Friday: Backup Verification
- [ ] Verify PostgreSQL automated backups
- [ ] Test backup restoration process
- [ ] Document any schema changes
- [ ] Update disaster recovery plans

## 🚀 Deployment Procedures

### Standard Deployment Process
1. **Local Testing**
   ```bash
   # Run tests locally
   cd backend
   pytest tests/
   ```

2. **Commit Changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. **Push to GitHub**
   ```bash
   git push origin main
   ```

4. **Monitor Deployment**
   - Watch Render dashboard for build progress
   - Check logs for any deployment errors
   - Verify health endpoints after deployment

### Rollback Procedure
If deployment fails:
1. Access Render dashboard
2. Navigate to ultrai-core → Deploy
3. Click "Rollback" to previous version
4. Verify system functionality

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

#### Issue: Frontend Can't Connect to Backend
**Symptoms**: Network errors in browser console
**Solution**:
1. Verify backend URL in vercel.json
2. Check CORS settings in backend
3. Ensure security headers aren't blocking requests

#### Issue: 500 Error on Orchestration
**Symptoms**: `/api/orchestrator/feather` returns 500
**Solution**:
1. Check LLM API keys are configured
2. Verify async/await patterns in orchestrator
3. Enable MOCK_MODE for testing

#### Issue: Health Endpoints Failing
**Symptoms**: Health checks return errors
**Solution**:
1. Check database connectivity
2. Verify Redis is running
3. Review middleware configuration

### Debug Commands
```bash
# Check backend logs
curl https://ultrai-core.onrender.com/api/health/detailed

# Test specific pattern
curl -X POST https://ultrai-core.onrender.com/api/orchestrator/feather \
  -H "Content-Type: application/json" \
  -d '{"pattern": "gut", "prompt": "test", "mock": true}'

# Verify model registry
curl https://ultrai-core.onrender.com/api/orchestrator/models
```

## 🚨 Emergency Procedures

### System Down Protocol
1. **Immediate Actions**
   - Check Render service status
   - Verify Vercel deployment status
   - Check PostgreSQL and Redis availability

2. **Communication**
   - Notify team via Slack/email
   - Update status page if available
   - Prepare incident report

3. **Recovery Steps**
   - Restart services via Render dashboard
   - Clear Redis cache if corrupted
   - Restore from backup if data issue

### Security Breach Response
1. **Contain**
   - Disable affected API keys immediately
   - Block suspicious IPs
   - Enable maintenance mode

2. **Investigate**
   - Review access logs
   - Check for unauthorized data access
   - Document timeline of events

3. **Remediate**
   - Rotate all secrets and keys
   - Update security patches
   - Implement additional monitoring

## ⚙️ Configuration Management

### Environment Variables
Location: Render Dashboard → Environment

**Critical Variables**:
```
DATABASE_URL          # PostgreSQL connection
REDIS_URL            # Redis cache connection
JWT_SECRET           # Authentication secret
ALLOWED_ORIGINS      # CORS configuration
```

**LLM Provider Keys** (when ready):
```
ANTHROPIC_API_KEY    # Claude API access
OPENAI_API_KEY       # GPT-4 access
GOOGLE_API_KEY       # Gemini access
```

### Configuration Updates
1. Always test in development first
2. Update one service at a time
3. Monitor logs during changes
4. Have rollback plan ready

### Monitoring Dashboards
- **Render**: https://dashboard.render.com
- **Vercel**: https://vercel.com/dashboard
- **PostgreSQL**: Via Render dashboard
- **Redis**: Via Render dashboard

## 📊 Key Metrics to Track

### System Health
- API response time < 500ms
- Error rate < 1%
- Uptime > 99.9%
- Health check success rate = 100%

### Performance
- Database query time < 100ms
- Cache hit rate > 80%
- Memory usage < 80%
- CPU usage < 70%

### Business Metrics
- Daily active users
- API calls per day
- Pattern usage distribution
- Feature adoption rates

## 🔐 Security Checklist

### Daily
- [ ] Review authentication logs
- [ ] Check for failed login attempts
- [ ] Verify SSL certificates

### Weekly
- [ ] Rotate API keys if needed
- [ ] Review security headers
- [ ] Check for vulnerabilities

### Monthly
- [ ] Security audit
- [ ] Penetration testing
- [ ] Update dependencies

## 📝 Maintenance Log Template

```markdown
Date: YYYY-MM-DD
Performed by: [Name]
Type: [Daily/Weekly/Emergency]

Tasks Completed:
- [ ] Task 1
- [ ] Task 2

Issues Found:
- None / Description

Actions Taken:
- Description of fixes

Next Steps:
- Follow-up items
```

## 🤝 Support Contacts

- **Technical Issues**: [Create GitHub issue]
- **Render Support**: support@render.com
- **Vercel Support**: support@vercel.com
- **Emergency**: [Team contact list]

---

Remember: Always document changes, test thoroughly, and maintain backups!
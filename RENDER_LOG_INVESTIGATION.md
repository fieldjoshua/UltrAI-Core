# Render Log Investigation Guide

## How to Access Logs

1. **Via Render Dashboard**:
   - Go to https://dashboard.render.com
   - Select the `ultrai-staging-api` service
   - Click on "Logs" tab
   - Look for recent errors or warnings

2. **Via Render CLI** (if installed):
   ```bash
   render logs ultrai-staging-api --tail
   ```

## What to Look For

### 1. LLM Service Degradation
Search for these keywords in logs:
- `degraded`
- `llm_service`
- `model_availability`
- `health_check`
- `rate_limit`
- `timeout`
- `connection refused`

### 2. Common LLM Issues

#### A. Rate Limiting
```
ERROR: Rate limit exceeded for OpenAI
ERROR: 429 Too Many Requests
WARNING: Throttling requests to provider
```

#### B. API Key Issues
```
ERROR: Invalid API key for provider
ERROR: Authentication failed
ERROR: 401 Unauthorized from provider
```

#### C. Timeout Issues
```
ERROR: Request to LLM provider timed out
ERROR: HTTPException: timeout
WARNING: Slow response from model
```

#### D. Initialization Failures
```
ERROR: Failed to initialize LLM service
ERROR: Could not connect to provider
ERROR: Model not available: [model_name]
```

### 3. Service Health Check Logic
Look for the health check implementation:
```python
# The service might be marked degraded if:
# - Any provider fails health check
# - Response time exceeds threshold
# - Minimum model requirement not met
```

### 4. Specific Error Patterns

#### During Startup
```
INFO: Starting LLM service...
ERROR: [specific error here]
WARNING: LLM service degraded: [reason]
```

#### During Health Checks
```
INFO: Performing health check
ERROR: Health check failed for [provider]
INFO: Marking service as degraded
```

## Log Analysis Script

Create this script to analyze downloaded logs:

```python
#!/usr/bin/env python3
import re
import sys
from collections import Counter

def analyze_logs(log_file):
    errors = []
    warnings = []
    llm_issues = []
    
    patterns = {
        'rate_limit': r'(rate.?limit|429|too.?many.?requests)',
        'timeout': r'(timeout|timed.?out|slow.?response)',
        'auth': r'(401|unauthorized|invalid.?api.?key|authentication)',
        'llm_error': r'(llm|model|provider).*(error|failed|degraded)',
        'health': r'health.?check.*(failed|degraded|unhealthy)'
    }
    
    with open(log_file, 'r') as f:
        for line in f:
            line_lower = line.lower()
            
            if 'error' in line_lower:
                errors.append(line.strip())
            elif 'warning' in line_lower:
                warnings.append(line.strip())
            
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, line_lower):
                    llm_issues.append((pattern_name, line.strip()))
    
    return errors, warnings, llm_issues

# Usage: python analyze_logs.py render_logs.txt
```

## Quick Checks via API

While waiting for logs, test these endpoints:

```bash
# Check specific provider availability
curl -s "https://ultrai-staging-api.onrender.com/api/models/check-availability?providers=openai,anthropic,google" | jq

# Get model recommendations (might show issues)
curl -s "https://ultrai-staging-api.onrender.com/api/models/recommendations" | jq

# Check cache status (might affect performance)
curl -s "https://ultrai-staging-api.onrender.com/api/metrics" | grep -i cache
```

## Common Fixes

### 1. Rate Limiting
- Implement exponential backoff
- Add request queuing
- Use different API keys for staging/prod

### 2. Timeout Issues
- Increase timeout settings
- Add retry logic
- Check network connectivity

### 3. Model Availability
- Verify API keys are correct
- Check provider service status
- Ensure models exist and are accessible

### 4. Health Check Logic
- Review health check criteria
- Adjust thresholds if too sensitive
- Add grace period for temporary issues

## Next Steps

1. **Download recent logs** (last 1-2 hours)
2. **Search for error patterns** listed above
3. **Identify root cause** of degradation
4. **Implement fix** based on findings
5. **Verify fix** by checking health endpoint

The LLM service degradation is likely due to one of:
- Rate limiting from providers
- Slow response times triggering health check failures
- Initialization issues with one or more providers
- Overly strict health check criteria
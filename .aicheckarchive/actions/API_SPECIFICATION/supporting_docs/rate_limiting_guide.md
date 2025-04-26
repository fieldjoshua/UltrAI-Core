# API Rate Limiting Guide

## Overview

This document details the rate limiting policies and implementation for the UltraAI API, including tier limits, quota management, and handling rate limit exceeded scenarios.

## Rate Limit Tiers

### Free Tier

- 10 requests per minute
- 1,000 requests per day
- Basic analysis patterns only
- No priority queuing

### Standard Tier

- 60 requests per minute
- 10,000 requests per day
- All analysis patterns
- Priority queuing
- Advanced features

### Enterprise Tier

- Custom limits based on agreement
- Unlimited requests
- All features
- Highest priority queuing
- Dedicated support

## Rate Limit Headers

The API includes rate limit information in response headers:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1616784000
```

### Header Descriptions

- `X-RateLimit-Limit`: Maximum requests allowed in the current period
- `X-RateLimit-Remaining`: Number of requests remaining in the current period
- `X-RateLimit-Reset`: Unix timestamp when the rate limit resets

## Quota Management

### Daily Quota

- Resets at midnight UTC
- Tracked per API key
- Can be viewed in the dashboard

### Monthly Quota

- Resets on the 1st of each month
- Based on subscription tier
- Can be upgraded at any time

## Handling Rate Limits

### Rate Limit Exceeded Response

```json
{
  "error": "rate_limit_exceeded",
  "error_description": "Too many requests",
  "retry_after": 60,
  "quota_reset": "2024-03-27T00:00:00Z"
}
```

### Best Practices

1. **Implement Exponential Backoff**

   ```python
   import time
   import random

   def make_request_with_backoff(url, max_retries=3):
       for attempt in range(max_retries):
           try:
               response = requests.get(url)
               if response.status_code == 429:
                   retry_after = int(response.headers.get('Retry-After', 60))
                   time.sleep(retry_after + random.uniform(0, 1))
                   continue
               return response
           except Exception as e:
               if attempt == max_retries - 1:
                   raise e
               time.sleep(2 ** attempt + random.uniform(0, 1))
   ```

2. **Monitor Rate Limits**

   ```python
   def check_rate_limits(response):
       remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
       reset_time = int(response.headers.get('X-RateLimit-Reset', 0))

       if remaining < 10:
           print(f"Warning: Only {remaining} requests remaining")
           print(f"Resets at: {time.ctime(reset_time)}")
   ```

3. **Implement Request Queuing**

   ```python
   from queue import Queue
   import threading

   class RateLimitedQueue:
       def __init__(self, max_requests=60, time_window=60):
           self.queue = Queue()
           self.max_requests = max_requests
           self.time_window = time_window
           self.requests = []
           self.lock = threading.Lock()

       def add_request(self, request):
           with self.lock:
               current_time = time.time()
               self.requests = [t for t in self.requests if current_time - t < self.time_window]

               if len(self.requests) >= self.max_requests:
                   self.queue.put(request)
               else:
                   self.requests.append(current_time)
                   return True
           return False
   ```

## Monitoring and Alerts

### Dashboard Metrics

- Current usage
- Quota remaining
- Peak usage times
- Error rates

### Alert Thresholds

- 80% of quota used
- Rate limit exceeded
- Unusual usage patterns

## Implementation Examples

### Python

```python
import requests
import time
from datetime import datetime

class UltraAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.ultra.ai"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        })

    def check_rate_limits(self, response):
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))

        if remaining < 10:
            print(f"Warning: Only {remaining} requests remaining")
            print(f"Resets at: {datetime.fromtimestamp(reset_time)}")

    def make_request(self, endpoint, method="GET", **kwargs):
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            return self.make_request(endpoint, method, **kwargs)

        self.check_rate_limits(response)
        return response
```

### JavaScript

```javascript
class UltraAPIClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = "https://api.ultra.ai";
    }

    async checkRateLimits(response) {
        const remaining = parseInt(response.headers.get('X-RateLimit-Remaining') || 0);
        const resetTime = parseInt(response.headers.get('X-RateLimit-Reset') || 0);

        if (remaining < 10) {
            console.warn(`Warning: Only ${remaining} requests remaining`);
            console.warn(`Resets at: ${new Date(resetTime * 1000)}`);
        }
    }

    async makeRequest(endpoint, method = 'GET', options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const response = await fetch(url, {
            method,
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Accept': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (response.status === 429) {
            const retryAfter = parseInt(response.headers.get('Retry-After') || 60);
            await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
            return this.makeRequest(endpoint, method, options);
        }

        await this.checkRateLimits(response);
        return response;
    }
}
```

## Related Documentation

- [API Specification Plan](../API_SPECIFICATION-PLAN.md)
- [Authentication Guide](./authentication_guide.md)
- [Deployment Guide](./deployment_guide.md)

## Last Updated

2024-03-26

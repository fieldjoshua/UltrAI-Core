# Authentication and Rate Limiting Implementation

## Overview
This document describes the P1 authentication and rate limiting implementation for UltrAI-Core.

## Authentication

### Configuration
- Controlled by `ENABLE_AUTH` environment variable (default: `true`)
- When enabled, protects `/api/admin/*` and `/api/debug/*` endpoints

### Authentication Methods
1. **JWT Bearer Tokens**
   - Header: `Authorization: Bearer <token>`
   - Used for user sessions after login
   - Tokens expire based on `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` setting

2. **API Keys**
   - Header: `X-API-Key: <key>`
   - Used for programmatic access
   - Keys are tied to user accounts and never expire unless revoked

### Protected Endpoints
- `/api/admin/*` - Admin operations
- `/api/debug/*` - Debug endpoints (environment variables, database config)

### Public Endpoints
- `/health`, `/api/health` - Health checks
- `/api/auth/*` - Authentication endpoints (login, register, refresh)
- `/api/docs`, `/api/redoc`, `/api/openapi.json` - API documentation
- `/api/analyze`, `/api/orchestrator` - Temporarily public for testing
- `/api/available-models`, `/api/pricing` - Public information endpoints

## Rate Limiting

### Configuration
- Controlled by `ENABLE_RATE_LIMIT` environment variable (default: `true`)
- Requires Redis for distributed rate limiting
- Falls back gracefully if Redis is unavailable

### Rate Limit Tiers
Based on user subscription tier:

| Tier | General API | Analyze API | Document API |
|------|------------|-------------|--------------|
| FREE | 60/min | 10/min | 5/min |
| BASIC | 300/min | 60/min | 30/min |
| PREMIUM | 1000/min | 120/min | 60/min |
| ENTERPRISE | 5000/min | 600/min | 300/min |

### Rate Limit Headers
All responses include:
- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Requests remaining in current window
- `X-RateLimit-Reset` - Unix timestamp when the window resets
- `Retry-After` - Seconds to wait (only on 429 responses)

### Rate Limit Behavior
- **Authenticated users**: Rate limited per user ID
- **API key requests**: Rate limited per API key
- **Unauthenticated requests**: Rate limited per IP address
- Returns `429 Too Many Requests` when limit exceeded

## Middleware Order
1. CORS middleware (handles preflight requests)
2. Authentication middleware (validates JWT/API keys)
3. Rate limiting middleware (enforces limits based on auth)

## Environment Variables

### Authentication
- `ENABLE_AUTH` - Enable/disable authentication (default: `true`)
- `JWT_SECRET` - Secret key for JWT signing
- `JWT_ALGORITHM` - JWT algorithm (default: `HS256`)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Access token expiry (default: `30`)

### Rate Limiting
- `ENABLE_RATE_LIMIT` - Enable/disable rate limiting (default: `true`)
- `REDIS_URL` - Redis connection URL (default: `redis://localhost:6379/0`)

## Testing

### Manual Testing
1. Test protected endpoint without auth:
   ```bash
   curl http://localhost:8000/api/admin/users
   # Should return 401
   ```

2. Test with valid token:
   ```bash
   TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password"}' \
     | jq -r '.access_token')
   
   curl http://localhost:8000/api/admin/users \
     -H "Authorization: Bearer $TOKEN"
   ```

3. Test rate limiting:
   ```bash
   # Make multiple requests quickly
   for i in {1..100}; do
     curl -I http://localhost:8000/api/analyze
   done
   # Should see 429 responses after limit exceeded
   ```

### Automated Tests
Run the test suite:
```bash
pytest tests/test_auth_rate_limit.py -v
```

## Security Considerations
1. JWT secrets must be rotated regularly in production
2. API keys should be treated as passwords
3. Rate limits should be monitored and adjusted based on usage patterns
4. Failed authentication attempts should be logged for security monitoring
5. Consider implementing IP-based blocking for repeated auth failures
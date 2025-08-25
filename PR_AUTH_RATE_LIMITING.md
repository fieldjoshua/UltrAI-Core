# PR: Auth & Rate Limiting Implementation (Issue #33)

## Summary
This PR implements authentication and rate limiting as specified in P1 requirements:
- ✅ ENABLE_AUTH=true now properly protects `/api/admin/*` and `/api/debug/*` endpoints
- ✅ Per-user rate limiting based on subscription tiers
- ✅ API key rate limiting support
- ✅ Combined authentication supporting both JWT tokens and API keys

## Implementation Details

### Authentication Middleware
- Created `CombinedAuthMiddleware` that supports both JWT Bearer tokens and API keys
- Admin and debug routes now require authentication when `ENABLE_AUTH=true`
- Public endpoints remain accessible without authentication
- Graceful fallback for database connectivity issues

### Rate Limiting
- Implemented per-user rate limiting with tier-based limits:
  - FREE: 60 req/min (general), 10 req/min (analyze), 5 req/min (documents)
  - BASIC: 300 req/min (general), 60 req/min (analyze), 30 req/min (documents)
  - PREMIUM: 1000 req/min (general), 120 req/min (analyze), 60 req/min (documents)
  - ENTERPRISE: 5000 req/min (general), 600 req/min (analyze), 300 req/min (documents)
- IP-based rate limiting for unauthenticated requests
- Proper rate limit headers in all responses
- Redis-based distributed rate limiting with graceful degradation

### Files Changed
- `app/app.py` - Added auth and rate limiting middleware
- `app/middleware/combined_auth_middleware.py` - New combined auth middleware
- `app/middleware/rate_limit_middleware.py` - New rate limiting middleware
- `app/middleware/__init__.py` - Export new middleware
- `app/middleware/auth_middleware.py` - Fixed user.is_active check
- `tests/test_auth_rate_limit.py` - Comprehensive test suite
- `documentation/auth_rate_limiting.md` - Implementation documentation

## Testing
Created comprehensive test suite covering:
- Public endpoints remain accessible
- Admin/debug endpoints require authentication
- JWT token authentication
- API key authentication
- Rate limit headers
- Per-user vs IP-based rate limiting
- Tier-based limits
- Environment variable controls

## Configuration
### Environment Variables
- `ENABLE_AUTH` - Enable/disable authentication (default: true)
- `ENABLE_RATE_LIMIT` - Enable/disable rate limiting (default: true)
- Redis configuration for distributed rate limiting

## Security Considerations
- JWT secrets must be properly configured in production
- API keys are treated as sensitive credentials
- Failed auth attempts are logged
- Rate limits prevent abuse

## Backward Compatibility
- No breaking changes to existing endpoints
- Authentication temporarily disabled for `/api/analyze` and `/api/orchestrator` for testing
- Graceful degradation when Redis unavailable

## Next Steps
- Enable authentication for `/api/analyze` and `/api/orchestrator` after frontend updates
- Consider implementing refresh token rotation
- Add metrics for rate limit hits
- Implement IP-based blocking for repeated auth failures
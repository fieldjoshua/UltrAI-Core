# Security Best Practices for Ultra

## Overview

This document outlines the security measures and best practices implemented in the Ultra project.

## Environment Variables

### Required Environment Variables

The following environment variables MUST be set for the application to run:

- `SECRET_KEY`: Application secret key for sessions and CSRF protection
- `JWT_SECRET`: Secret key for signing JWT tokens
- `API_KEY_ENCRYPTION_KEY`: Key for encrypting stored API keys (required in production)

### Setting Environment Variables

1. Copy `.env.example` to `.env`
2. Generate secure secrets using:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(64))"
   ```
3. Never commit `.env` files or secrets to version control

## Authentication

### JWT Tokens

- Access tokens expire after 30 minutes by default
- Refresh tokens expire after 7 days
- All tokens are signed with the `JWT_SECRET`
- Token blacklist is maintained for logout functionality

### Password Security

- Passwords are hashed using bcrypt
- Minimum password requirements are enforced
- Password reset tokens expire after 1 hour

## API Key Storage

- LLM API keys are encrypted at rest using `API_KEY_ENCRYPTION_KEY`
- Keys are never logged or exposed in error messages
- API key availability is exposed without revealing the actual keys

## Security Headers

When `ENABLE_SECURITY_HEADERS=true` (default):

- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security (when HTTPS is enabled)
- X-XSS-Protection: 1; mode=block

## Rate Limiting

When `ENABLE_RATE_LIMIT=true` (default):

- API endpoints are rate-limited to prevent abuse
- Different limits apply to authentication endpoints

## CORS Configuration

- Default: All origins allowed in development
- Production: Specify allowed origins with `CORS_ORIGINS`

## Database Security

- SQL injection prevention through SQLAlchemy ORM
- Database credentials should use environment variables
- Use SSL/TLS for database connections in production

## File Upload Security

- File type validation
- Size limits enforced
- Files are scanned for malicious content
- Uploaded files stored outside web root

## Monitoring and Logging

- Security events are logged
- Failed authentication attempts are tracked
- Sensitive data is never logged
- Consider using Sentry for error tracking in production

## Development vs Production

### Development Mode

- More permissive CORS settings
- Debug mode may be enabled
- Mock authentication available for testing

### Production Mode

- All security features must be enabled
- No default secrets allowed
- HTTPS should be enforced
- Strict CORS origins

## Security Checklist

Before deploying to production:

- [ ] All environment variables set with secure values
- [ ] No default or test credentials in code
- [ ] Database using SSL/TLS
- [ ] HTTPS enabled
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] CORS origins properly restricted
- [ ] Error messages don't expose sensitive information
- [ ] Logging configured without sensitive data
- [ ] Regular security updates for dependencies

## Incident Response

1. Rotate all affected secrets immediately
2. Update all deployed environments
3. Review logs for unauthorized access
4. Notify affected users if necessary
5. Document incident and remediation steps

## Regular Security Tasks

- Review and update dependencies monthly
- Rotate secrets quarterly
- Audit authentication logs
- Review and update this documentation

---

Last Updated: 2025-05-17
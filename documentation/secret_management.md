# Secret Management and Security

## Overview
This document describes the secret management and security scanning implementation for UltrAI-Core.

## Secret Rotation

### Automated Secret Rotation Script
Use the provided script to rotate secrets:
```bash
python scripts/rotate_secrets.py
```

This script:
1. Generates new cryptographically secure secrets
2. Creates a backup of existing .env file
3. Updates .env.example with placeholders
4. Checks for hardcoded secrets in code
5. Provides instructions for updating production environments

### Manual Secret Rotation
If rotating secrets manually:
1. Generate new secrets using secure methods:
   ```python
   import secrets
   jwt_secret = secrets.token_urlsafe(64)
   api_key = f"ultra_{secrets.token_urlsafe(32)}"
   ```
2. Update all deployment environments (Render, GitHub Secrets, etc.)
3. Consider gradual rollout to avoid invalidating existing sessions

## CI/CD Secret Scanning

### GitHub Actions Workflow
The `.github/workflows/secret-scanning.yml` workflow runs on:
- Every push to main/develop branches
- All pull requests
- Manual workflow dispatch

It performs:
1. **TruffleHog scanning** - Scans entire git history for secrets
2. **GitLeaks scanning** - Additional secret detection with custom rules
3. **Python hardcoded secret check** - Specific patterns in Python files
4. **Frontend bundle check** - Ensures no secrets in built JS files
5. **.env.example validation** - Ensures only placeholders, no real secrets

### Custom GitLeaks Configuration
`.gitleaks.toml` defines:
- Custom rules for JWT secrets, API keys, and UltrAI-specific patterns
- Allowlists for development fallback secrets in specific files
- Exclusions for test files and example values

## Pre-commit Hooks

### Installation
```bash
pip install pre-commit
pre-commit install
```

### Hooks Configured
1. **Gitleaks** - Prevents committing secrets
2. **Custom secret check** - Additional Python-specific checks
3. **Bandit** - Python security linting
4. **Ruff** - Code quality and formatting
5. **Standard checks** - YAML validation, large files, merge conflicts

### Running Manually
```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run gitleaks --all-files
```

## Environment Variables

### Required Secrets
Production environment must set:
- `JWT_SECRET` / `JWT_SECRET_KEY` - JWT signing key
- `JWT_REFRESH_SECRET` / `JWT_REFRESH_SECRET_KEY` - Refresh token key
- `SECRET_KEY` - General app secret
- `API_KEY_ENCRYPTION_KEY` - For encrypting stored API keys
- `CSRF_SECRET_KEY` - CSRF protection

### Development Fallbacks
- Development environments use secure fallback values
- These are only loaded when `ENVIRONMENT != production`
- Production will fail to start without proper secrets

## Frontend Security

### Build-time Security
- No secrets are embedded in frontend bundles
- API URLs are configured via environment variables
- Build process validates no secret patterns in output

### Runtime Security
- Tokens stored in sessionStorage (cleared on tab close)
- Refresh tokens in localStorage (for persistence)
- Automatic token refresh before expiry
- Secure context detection (HTTPS enforcement)

## Best Practices

### Do's
1. ✅ Always use environment variables for secrets
2. ✅ Rotate secrets regularly (quarterly minimum)
3. ✅ Use cryptographically secure generation methods
4. ✅ Different secrets for each environment
5. ✅ Monitor for exposed secrets in logs

### Don'ts
1. ❌ Never commit real secrets to git
2. ❌ Don't use predictable or weak secrets
3. ❌ Avoid logging secret values
4. ❌ Don't share secrets via insecure channels
5. ❌ Never embed secrets in frontend code

## Security Checklist

Before deploying:
- [ ] All secrets loaded from environment variables
- [ ] No hardcoded secrets in code (run `python scripts/rotate_secrets.py`)
- [ ] CI secret scanning passing
- [ ] Pre-commit hooks installed and passing
- [ ] Production environment variables updated
- [ ] Frontend build contains no secrets
- [ ] .env.example contains only placeholders

## Incident Response

If a secret is exposed:
1. **Immediate**: Rotate the affected secret
2. **Assess**: Check logs for unauthorized usage
3. **Update**: Deploy new secrets to all environments
4. **Notify**: Inform team and affected users if necessary
5. **Review**: Analyze how exposure occurred and prevent recurrence

## Testing

### Manual Testing
```bash
# Check for hardcoded secrets
grep -r "SECRET.*=.*['\"]" --include="*.py" .

# Validate .env.example
grep -E "=.+[a-zA-Z0-9]{20,}" .env.example

# Check frontend bundles
grep -i "api_key\|secret\|token" frontend/dist/assets/*.js
```

### Automated Testing
- CI runs on every push/PR
- Pre-commit hooks run before every commit
- Production deployment validates environment variables
# UltraAI Configuration Options

## Overview

This document details all configurable options for the UltraAI system. Configuration is managed through environment variables and can be overridden in different environments.

## Environment Variables

### Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection string | `sqlite:///./ultra.db` | Yes |
| `DATABASE_POOL_SIZE` | Connection pool size | `5` | No |
| `DATABASE_MAX_OVERFLOW` | Maximum overflow connections | `10` | No |
| `DATABASE_ECHO` | Enable SQL query logging | `False` | No |

### Authentication

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | JWT signing key | - | Yes |
| `ALGORITHM` | JWT algorithm | `HS256` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `1440` | No |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration | `30` | No |
| `PASSWORD_MIN_LENGTH` | Minimum password length | `8` | No |
| `PASSWORD_MAX_LENGTH` | Maximum password length | `128` | No |

### API Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_V1_PREFIX` | API version prefix | `/api/v1` | No |
| `PROJECT_NAME` | Project name | `UltraAI` | No |
| `BACKEND_CORS_ORIGINS` | CORS allowed origins | `[]` | No |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `100` | No |

### Logging

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `LOG_FORMAT` | Log format | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | No |
| `LOG_FILE` | Log file path | `ultra.log` | No |
| `LOG_ROTATION` | Log rotation size | `10MB` | No |

### Security

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_HTTPS` | Enable HTTPS | `True` | No |
| `SSL_CERT_PATH` | SSL certificate path | - | If HTTPS enabled |
| `SSL_KEY_PATH` | SSL key path | - | If HTTPS enabled |
| `ALLOWED_HOSTS` | Allowed hostnames | `["*"]` | No |

### Cache Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CACHE_TYPE` | Cache backend type | `memory` | No |
| `CACHE_TTL` | Cache time-to-live | `3600` | No |
| `REDIS_URL` | Redis URL (if using Redis) | - | If using Redis |

### Email Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SMTP_HOST` | SMTP server host | - | If email enabled |
| `SMTP_PORT` | SMTP server port | `587` | If email enabled |
| `SMTP_USER` | SMTP username | - | If email enabled |
| `SMTP_PASSWORD` | SMTP password | - | If email enabled |
| `EMAILS_FROM_EMAIL` | From email address | - | If email enabled |
| `EMAILS_FROM_NAME` | From name | `UltraAI` | If email enabled |

## Configuration Loading

The system loads configuration in the following order:

1. Default values
2. Environment variables
3. `.env` file
4. Command-line arguments

## Environment-Specific Configuration

### Development

```bash
# .env.development
DATABASE_URL=sqlite:///./ultra_dev.db
LOG_LEVEL=DEBUG
DATABASE_ECHO=True
```

### Testing

```bash
# .env.test
DATABASE_URL=sqlite:///./ultra_test.db
LOG_LEVEL=DEBUG
TESTING=True
```

### Production

```bash
# .env.production
DATABASE_URL=postgresql://user:pass@localhost/ultra
LOG_LEVEL=WARNING
ENABLE_HTTPS=True
```

## Configuration Validation

The system validates all configuration values on startup. Invalid configurations will cause the application to fail fast with clear error messages.

## Security Considerations

1. Never commit sensitive configuration values to version control
2. Use environment variables for secrets
3. Rotate secrets regularly
4. Use different configurations for different environments
5. Validate all configuration values

## Best Practices

1. Use environment-specific configuration files
2. Document all configuration options
3. Provide sensible defaults
4. Validate configuration values
5. Use type-safe configuration loading
6. Implement configuration hot-reloading where appropriate

## Troubleshooting

### Common Issues

1. **Configuration Not Loading**
   - Check environment variable names
   - Verify `.env` file location
   - Check file permissions

2. **Invalid Configuration**
   - Review validation errors
   - Check data types
   - Verify required values

3. **Environment-Specific Issues**
   - Verify environment selection
   - Check environment-specific files
   - Validate environment variables

## Support

For configuration support:

1. Check this documentation
2. Review environment-specific guides
3. Contact the development team
4. Create a new issue if needed

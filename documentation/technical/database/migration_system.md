# Database Migration System

This document provides an overview of the database migration system implemented in the Ultra project.

## Overview

The migration system in Ultra enables reliable schema evolution across environments, with safeguards to prevent data loss and ensure consistent application of schema changes.

## Features

- **Alembic Integration**: Built on the industry-standard Alembic framework
- **Safety Features**: Automatic backups, validation checks, and dry-run capability
- **CLI Tools**: Comprehensive management tools for migrations
- **Health Integration**: Migration status in system health checks
- **CI/CD Support**: Tools for migration verification in CI/CD pipelines
- **Documentation**: Clear guidelines and troubleshooting documentation

## Component Architecture

![Migration Architecture](https://mermaid.ink/img/pako:eNp1kstuwjAQRX9l5FWQkgVhkVUlFqgLEKraRbsoSYzxyIlHjoOgEf-eCaHloSy8mXvPzJ17vWckUgLRiMK8rkFZbyhT5JtmUoL-MYUe7lYPiuSjQzK5EM894OJHIJGUQs_PVHuLbYSXEsYUu1SryMZm24CGKkZSNI7v4UhcQSlshuwVtj3uf2GhpHVv-mA1ZWVNj-RvQPswAVkT9Dqu2KJdLs4ZKK_wFFJgYgfbcH04oYlSpdkzv3MvnxB5J9f26LKhxgMNRMVyxhTgV3-S87MQXgpjO4hR6sKbQOHIOqJX3J4rFE68-9-fTuNGz1Coc6_M6B2Jg64swbaqK9W6ynQF_LCNRLMvkPGMQVnv6vGK8F-4n48rGHy0kUq9K1T7N6uhEBnEPIvXiW_zNIl3i5QHQRJm6SrOVmmY7LJ8F2z8B9dwgf4?type=png)

### Key Components

1. **Schema Definitions**: SQLAlchemy ORM models define the database schema
2. **Migration Engine**: Alembic provides the core migration framework
3. **Migration Scripts**: Generated scripts in the versions directory
4. **CLI Tools**: Migration management and operations tools
5. **Health Check Integration**: Migration status monitoring
6. **CI/CD Integration**: Pipeline verification tools
7. **Safety Mechanisms**: Backups and validation checks

## Usage

### Basic Operations

```bash
# Check migration status
./scripts/db_migrate.sh status

# Generate a new migration
./scripts/db_migrate.sh generate "Add user preferences"

# Generate an auto-migration from model changes
./scripts/db_migrate.sh auto "Add user preferences"

# Apply pending migrations
./scripts/db_migrate.sh upgrade

# Revert a migration
./scripts/db_migrate.sh downgrade -1
```

### Safety Features

```bash
# Create database backup
./scripts/db_migrate.sh backup

# Restore from backup
./scripts/db_migrate.sh restore backups/backup_20250501.sql

# Validate migration integrity
./scripts/db_migrate.sh verify
```

### CI/CD Integration

```bash
# Check for pending migrations in CI pipeline
python scripts/check_migrations.py --fail-on-pending --json
```

## Directory Structure

```
/backend/database/migrations/
├── __init__.py            # Package initialization
├── db_migrate.py          # Migration CLI tool
├── env.py                 # Alembic environment
├── init_migrations.py     # Migration initialization tool
├── migration_health.py    # Health check integration
├── script.py.mako         # Template for migration files
└── versions/              # Directory for migration versions
    └── README.md          # Documentation for versions

/scripts/
├── db_migrate.sh          # Migration wrapper script
├── start-migrate.sh       # Start script with migration handling
└── check_migrations.py    # CI/CD migration verification

/documentation/database/
├── migration_guidelines.md    # Best practices
├── migration_system.md        # System overview
└── migration_troubleshooting.md  # Troubleshooting guide
```

## Best Practices

1. **Small Focused Migrations**: Create small, focused migrations rather than large schema changes
2. **Transactional Migrations**: Ensure changes are applied atomically
3. **Version Control**: Keep migrations in version control with application code
4. **Testing**: Test migrations in development before deploying to production
5. **Backups**: Always create backups before applying migrations in production
6. **Validation**: Use verification tools to check migration integrity

## Configuration

The migration system is configured in the following files:

- `/alembic.ini`: Root configuration file
- `/backend/database/alembic.ini`: Detailed migration settings
- `/backend/database/migrations/env.py`: Alembic environment configuration

Key configuration options:

```ini
# Database URL (overridden by environment variables)
sqlalchemy.url = postgresql://ultrauser:ultrapassword@localhost:5432/ultra

# Migration file template
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(slug)s

# Transaction per migration
transaction_per_migration = true

# Schema comparison options
compare_type = true
compare_server_default = true
```

## Integration with Health Checks

The migration system integrates with the health check system:

```python
# Health check registration
from backend.utils.health_check import HealthCheck, ServiceType
from backend.database.migrations.migration_health import check_migration_health

# Create migration health check
migration_check = HealthCheck(
    name="database_migrations",
    service_type=ServiceType.DATABASE,
    check_fn=check_migration_health,
    description="Database migration status",
    is_critical=False,
)
```

Health check endpoints now include migration status information.

## Conclusion

The database migration system provides a robust foundation for evolving the Ultra application's database schema. It ensures reliability, safety, and transparency in schema changes across all environments.

# Database Migrations

This directory contains database migration scripts for the Ultra project using Alembic.

## Directory Structure

- `env.py`: Alembic environment configuration
- `script.py.mako`: Template for migration scripts
- `versions/`: Directory containing individual migration versions

## Migration Workflow

### Generating a New Migration

```bash
# Generate a new migration
python -m backend.database.migrations.db_migrate generate "description_of_changes"
```

### Applying Migrations

```bash
# Apply all pending migrations
python -m backend.database.migrations.db_migrate upgrade

# Apply migrations up to a specific version
python -m backend.database.migrations.db_migrate upgrade <revision>
```

### Reverting Migrations

```bash
# Revert the last migration
python -m backend.database.migrations.db_migrate downgrade -1

# Revert to a specific version
python -m backend.database.migrations.db_migrate downgrade <revision>
```

### Checking Migration Status

```bash
# Check current migration status
python -m backend.database.migrations.db_migrate status
```

## Best Practices

1. Always test migrations in a development environment before applying to production
2. Create small, focused migrations rather than large schema changes
3. Include both "upgrade" and "downgrade" logic in each migration
4. Use transactional migrations whenever possible
5. Be cautious with data migrations that modify existing data

## Further Documentation

For more detailed information, see:

- [Migration Guidelines](/documentation/database/migration_guidelines.md)
- [Troubleshooting Migrations](/documentation/database/migration_troubleshooting.md)
- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)

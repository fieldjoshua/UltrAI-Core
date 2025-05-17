# Database Migration Guidelines

This document provides guidelines for working with database migrations in the Ultra project. Following these practices ensures reliable database schema evolution and prevents common issues during deployments.

## Migration Architecture

The Ultra project uses [Alembic](https://alembic.sqlalchemy.org/en/latest/) for database migrations, integrated with SQLAlchemy models. The migration system is organized as follows:

### Directory Structure

```
/backend/database/migrations/
├── env.py              # Alembic environment configuration
├── migration_health.py # Health check for migrations
├── db_migrate.py       # Migration CLI tool
├── script.py.mako      # Template for migration files
└── versions/           # Directory for migration version files
```

### Configuration

- **Root alembic.ini**: `/alembic.ini` (points to backend configuration)
- **Backend alembic.ini**: `/backend/database/alembic.ini` (actual configuration)

## Working with Migrations

### Generating Migrations

Migrations can be generated automatically based on SQLAlchemy model changes:

```bash
# From the project root
python -m backend.database.migrations.db_migrate generate "Added user preferences"
```

This creates a new migration file in the `versions/` directory. For auto-generation:

```bash
python -m backend.database.migrations.db_migrate generate "Added user preferences" --autogenerate
```

### Applying Migrations

Migrations are typically applied automatically during application startup, but can be manually applied:

```bash
# Apply all pending migrations
python -m backend.database.migrations.db_migrate upgrade

# Apply migrations up to a specific revision
python -m backend.database.migrations.db_migrate upgrade <revision_id>
```

### Checking Migration Status

To check the current migration status:

```bash
python -m backend.database.migrations.db_migrate status
```

### Reverting Migrations

Migrations can be reverted if necessary:

```bash
# Revert the last migration
python -m backend.database.migrations.db_migrate downgrade -1

# Revert to a specific revision
python -m backend.database.migrations.db_migrate downgrade <revision_id>
```

## Best Practices

### 1. Keep Migrations Small and Focused

Each migration should make a small, focused change to the database schema. This makes migrations easier to understand, test, and revert if necessary.

```python
# Good - focused on one change
def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))

# Avoid - too many unrelated changes
def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.add_column('products', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default=sa.text('false')))
```

### 2. Always Include Downgrade Logic

Every migration should include both upgrade and downgrade functionality to enable rollbacks.

```python
def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))

def downgrade():
    op.drop_column('users', 'email_verified')
```

### 3. Use Transactional Migrations

Migrations should be transactional whenever possible to ensure atomicity. The default Alembic configuration in this project enables transaction-per-migration.

### 4. Be Careful with Data Migrations

Data migrations can be slow and error-prone. Consider these guidelines:

- Use batch processing for large tables
- Include progress reporting for long-running migrations
- Consider implementing data migrations as separate application code for complex cases

```python
def upgrade():
    # Schema change
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))

    # Data migration with batching
    connection = op.get_bind()
    offset = 0
    batch_size = 1000

    while True:
        users = connection.execute(
            sa.text(f"SELECT id, first_name, last_name FROM users LIMIT {batch_size} OFFSET {offset}")
        ).fetchall()

        if not users:
            break

        for user in users:
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            connection.execute(
                sa.text("UPDATE users SET full_name = :full_name WHERE id = :id"),
                {"full_name": full_name, "id": user.id}
            )

        offset += batch_size
```

### 5. Test Migrations Before Deployment

Always test migrations in a development or staging environment before applying them to production:

```bash
# Test migrations without applying them
python -m backend.database.migrations.db_migrate upgrade --sql
```

### 6. Backup Before Migrating

Before applying migrations in production, create a database backup:

```bash
python -m backend.database.migrations.db_migrate backup
python -m backend.database.migrations.db_migrate upgrade --backup
```

### 7. Avoid Altering Primary Keys

Changing primary keys can be problematic due to foreign key constraints. If you need to change a primary key:

- Create a new table with the desired structure
- Copy data from the old table to the new table
- Update foreign keys to point to the new table
- Drop the old table
- Rename the new table to the original name

### 8. Handle Nullable Constraints Carefully

When adding a non-nullable column, always provide a default value:

```python
# Good - provides default value
op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')))

# Bad - will fail if table has existing data
op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False))
```

## Troubleshooting

### Common Issues

1. **Migration conflicts**: If you get "Multiple head revisions", you need to merge the heads:

   ```bash
   alembic merge -m "Merge multiple heads" <revision1> <revision2>
   ```

2. **Failed migrations**: If a migration fails, Alembic will roll back the transaction. Check the error message for details.

3. **Schema drift**: If the database schema doesn't match what Alembic expects, you may need to stamp the database with the current revision:
   ```bash
   python -m backend.database.migrations.db_migrate verify
   ```

### Getting Help

For further assistance with migrations:

- Check the [Alembic documentation](https://alembic.sqlalchemy.org/en/latest/)
- Review existing migration files in `versions/` for examples
- Consult the database team for complex migrations

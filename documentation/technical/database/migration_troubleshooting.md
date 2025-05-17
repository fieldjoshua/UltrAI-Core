# Database Migration Troubleshooting Guide

This guide provides solutions for common issues encountered with database migrations in the Ultra project.

## Diagnosing Migration Issues

### Check Migration Status

The first step in troubleshooting is to check the current migration status:

```bash
python -m backend.database.migrations.db_migrate status
```

This shows:

- Current revision
- Number of migrations applied
- Pending migrations (if any)

### Detailed Migration Information

For more detailed information about migrations:

```bash
python -m backend.database.migrations.db_migrate history -v
```

## Common Issues and Solutions

### 1. Multiple Head Revisions

**Symptom**: Error message like "Multiple head revisions: 1a2b3c, 4d5e6f"

**Cause**: This occurs when multiple migration branches have been created, often due to migrations being created simultaneously by different developers.

**Solution**:

1. Merge the heads:

   ```bash
   alembic -c alembic.ini merge -m "Merge multiple heads" 1a2b3c 4d5e6f
   ```

2. Apply the merged migration:
   ```bash
   python -m backend.database.migrations.db_migrate upgrade head
   ```

### 2. Failed Migration

**Symptom**: Error during migration with a specific error message

**Cause**: Most commonly due to data integrity issues, invalid SQL, or conflicts with existing schema

**Solution**:

1. Review the error message to understand the specific issue

2. If you need to revert a failed migration:

   ```bash
   python -m backend.database.migrations.db_migrate downgrade -1
   ```

3. Fix the migration file in the `versions/` directory

4. Apply the fixed migration:

   ```bash
   python -m backend.database.migrations.db_migrate upgrade head
   ```

5. If you need to restore from backup:
   ```bash
   python -m backend.database.migrations.db_migrate restore /path/to/backup.sql
   ```

### 3. Schema Drift

**Symptom**:

- Errors like "Table X exists but not in metadata"
- "Column Y exists in the database but not in the model"

**Cause**: The database schema has diverged from what Alembic expects, often due to manual changes or incomplete migrations

**Solution**:

1. Generate a migration that will bring the models in sync with the database:

   ```bash
   python -m backend.database.migrations.db_migrate generate "Sync models with database" --autogenerate
   ```

2. Carefully review the generated migration to ensure it will make the correct changes

3. Apply the migration:
   ```bash
   python -m backend.database.migrations.db_migrate upgrade head
   ```

### 4. Migration Command Not Found

**Symptom**: "Command not found" or similar error when running migration commands

**Cause**: Missing executable permissions or Python path issues

**Solution**:

1. Make sure the migration script is executable:

   ```bash
   chmod +x backend/database/migrations/db_migrate.py
   ```

2. Ensure you're running the command from the project root:

   ```bash
   # Correct
   python -m backend.database.migrations.db_migrate status

   # Incorrect
   cd backend && python database/migrations/db_migrate.py status
   ```

### 5. Alembic Version Mismatch

**Symptom**: Error message about Alembic version or incompatible migration format

**Cause**: Different versions of Alembic used to create and run migrations

**Solution**:

1. Check the installed Alembic version:

   ```bash
   pip show alembic
   ```

2. Make sure all developers are using the same version specified in requirements.txt

### 6. Pending Migrations on Startup

**Symptom**: Application fails to start with message about pending migrations

**Cause**: The application is configured to check for pending migrations on startup

**Solution**:

1. Apply pending migrations:

   ```bash
   python -m backend.database.migrations.db_migrate upgrade head
   ```

2. If you want to allow the application to start without applying migrations:
   ```bash
   export ALLOW_PENDING_MIGRATIONS=true
   ```

### 7. Foreign Key Constraint Violations

**Symptom**: Error about foreign key constraint violations during migration

**Cause**: Attempting to drop or modify tables or columns that are referenced by foreign keys

**Solution**:

1. For complex schema changes involving foreign keys, use a multi-step approach:

   ```python
   # Step 1: Drop the foreign key constraint
   def upgrade():
       op.drop_constraint('fk_posts_user_id_users', 'posts', type_='foreignkey')

   # Step 2: Modify the referenced table
   def upgrade():
       op.alter_column('users', 'id', existing_type=sa.Integer(), type_=sa.BigInteger())

   # Step 3: Recreate the foreign key with updated specifications
   def upgrade():
       op.create_foreign_key('fk_posts_user_id_users', 'posts', 'users', ['user_id'], ['id'])
   ```

2. Create separate migration files for each step

### 8. Data Type Conversion Issues

**Symptom**: Error about data type conversion during migration

**Cause**: Attempting to change a column type with data that can't be converted

**Solution**:

1. Clean up or transform the data before changing the type:

   ```python
   def upgrade():
       # First, clean up the data
       op.execute("UPDATE users SET phone_number = NULL WHERE phone_number = ''")

       # Then change the type
       op.alter_column('users', 'phone_number',
                      existing_type=sa.String(),
                      type_=sa.Integer(),
                      postgresql_using='phone_number::integer')
   ```

2. For complex data transformations, consider using a temporary column:

   ```python
   def upgrade():
       # Add temporary column
       op.add_column('users', sa.Column('phone_number_int', sa.Integer(), nullable=True))

       # Transform data
       op.execute("UPDATE users SET phone_number_int = phone_number::integer WHERE phone_number ~ '^[0-9]+$'")

       # Drop old column
       op.drop_column('users', 'phone_number')

       # Rename new column
       op.alter_column('users', 'phone_number_int', new_column_name='phone_number')
   ```

## Advanced Troubleshooting

### Database Locking Issues

If you encounter database locking issues during migrations:

1. Check for long-running transactions:

   ```sql
   SELECT * FROM pg_stat_activity WHERE state = 'active';
   ```

2. Consider scheduling migrations during low-traffic periods

3. For PostgreSQL, consider using the `--lock-timeout` option:
   ```bash
   export PGLOCK_TIMEOUT=10000  # 10 seconds
   python -m backend.database.migrations.db_migrate upgrade head
   ```

### Recreating the Migration Environment

If your migration environment becomes corrupted:

1. Create a database backup:

   ```bash
   python -m backend.database.migrations.db_migrate backup -o before_reset.sql
   ```

2. Reset the Alembic version table:

   ```sql
   DROP TABLE alembic_version;
   ```

3. Reinitialize migrations with the current schema:
   ```bash
   python -m backend.database.migrations.init_migrations
   ```

### Performance Issues with Large Tables

For migrations involving large tables:

1. Use batching for data migrations
2. Consider running migrations during off-peak hours
3. For PostgreSQL, consider using the `CONCURRENTLY` option for index creation:
   ```python
   def upgrade():
       op.execute(
           "CREATE INDEX CONCURRENTLY ix_users_email ON users (email)"
       )
   ```

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [Alembic documentation](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
2. Review the error logs in `logs/migration_health.log`
3. Contact the database team for assistance with complex migration issues

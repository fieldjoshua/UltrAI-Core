# Ultra Database Layer

This directory contains the database models, migrations, and schemas for the Ultra AI Framework backend.

## Directory Structure

- **migrations/**: Database migration scripts
  - Versioned database schema changes
  - Data migration utilities

- **schemas/**: Database schema definitions
  - Table definitions
  - Relationship mappings
  - Indexes and constraints

## Models

The Ultra backend uses SQLAlchemy ORM for database operations. Key models include:

- **Users**: User accounts and authentication
- **Analyses**: Stored analysis results
- **Documents**: Uploaded document metadata
- **Patterns**: Analysis pattern configurations
- **ModelConfigs**: LLM model configurations
- **Usage**: API usage tracking and billing

## Migrations

Database migrations are managed using Alembic. To run migrations:

```bash
cd backend
alembic upgrade head
```

To create a new migration:

```bash
alembic revision -m "description_of_changes"
```

## Connection Configuration

Database connection settings are configured in the `.env` file in the config directory. Example configuration:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ultra
DB_USER=ultrauser
DB_PASSWORD=securepassword
```

## Development

When making changes to the database schema:

1. Modify the appropriate model in the `schemas/` directory
2. Generate a migration using Alembic
3. Test the migration in a development environment
4. Include the migration script in your commit

## Backup and Restore

Database backup scripts are located in the `scripts/` directory:

- `backup_db.sh`: Creates a backup of the database
- `restore_db.sh`: Restores the database from a backup

## Testing

Database tests can be run using:

```bash
cd tests
pytest test_db.py
```

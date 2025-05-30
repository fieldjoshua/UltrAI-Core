# Migration Versions

This directory contains individual migration version files generated by Alembic.

## File Naming Convention

Migration files follow the Alembic naming convention:

```
<revision_id>_<slug>.py
```

Where:
- `revision_id` is a unique identifier generated by Alembic
- `slug` is a brief description of the migration (underscores instead of spaces)

## Migration File Structure

Each migration file contains:

1. **Revision identifiers**: Current revision ID, down revision ID
2. **Dependencies**: Other migrations this one depends on
3. **Creation timestamp**: When the migration was generated
4. **Description**: Brief explanation of the migration purpose
5. **Upgrade function**: Code to apply the migration
6. **Downgrade function**: Code to revert the migration

## Order of Execution

Migrations are applied in order based on their dependency chain, not their file names.
Alembic maintains a linear history by default but supports branching if needed.

## Important Notes

- Do not manually edit the revision IDs or dependencies
- Always include downgrade logic to enable rollbacks
- Test migrations thoroughly before applying to production
- For complex data migrations, consider breaking them into smaller steps

Refer to the main README.md file in the parent directory for usage instructions.

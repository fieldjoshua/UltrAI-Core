# Ultra Data Directory

This directory contains persistent data storage for the Ultra AI Framework.

## Directory Structure

- **embeddings/**: Vector embeddings for documents and queries
  - Used by the document processing system for semantic search
  - Generated using text-embedding models

- **cache/**: Cached responses and API results
  - Reduces duplicate API calls
  - Improves performance for repeated queries

- **results/**: Analysis results and outputs
  - Stored in structured format
  - Used for benchmarking and improvement

## Data Management

Data in this directory is organized by date and session ID to allow for easy tracking of analysis over time. This structure supports both debugging and performance benchmarking.

### Data Retention

By default, data is retained for 30 days. To change this behavior, modify the `DATA_RETENTION_DAYS` setting in the configuration file.

### Large Files

Large embedding files and result sets are stored with versioning to track changes over time. This directory is excluded from Git through the `.gitignore` file.

## Backups

Automated backups of this directory are configured in the `deployment/` scripts. To manually backup this data:

```bash
scripts/backup_data.sh [destination]
```

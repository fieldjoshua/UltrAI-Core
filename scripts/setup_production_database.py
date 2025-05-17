#!/usr/bin/env python3
"""Setup and verify production database configuration."""

import os
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config_database import get_database_config, test_database_connection
from backend.database import init_db
from backend.utils.logging import get_logger

logger = get_logger("database_setup")


def setup_production_database():
    """Setup and verify production database."""
    print("Production Database Setup")
    print("=" * 40)
    
    # Check if DATABASE_URL is set
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL to your production database connection string")
        print("Example: postgresql://user:password@host:port/database")
        return False
    
    print(f"Database URL configured: {db_url.split('@')[0]}@...")  # Hide credentials
    
    # Get database configuration
    db_config = get_database_config()
    
    # Test connection
    print("\nTesting database connection...")
    if test_database_connection(db_config):
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
        return False
    
    # Initialize database (create tables)
    try:
        print("\nInitializing database schema...")
        init_db()
        print("✓ Database schema initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {str(e)}")
        return False
    
    # Run migrations
    try:
        print("\nChecking for pending migrations...")
        from backend.database.migrations.migration_health import check_migrations
        
        migration_status = check_migrations()
        if migration_status["pending_migrations"]:
            print(f"Found {len(migration_status['pending_migrations'])} pending migrations")
            print("Run: alembic upgrade head")
        else:
            print("✓ All migrations applied")
    except Exception as e:
        print(f"Migration check failed: {str(e)}")
    
    print("\nDatabase setup complete!")
    print("\nConfiguration summary:")
    print(f"- Pool size: {db_config.get('pool_size', 'default')}")
    print(f"- Max overflow: {db_config.get('max_overflow', 'default')}")
    print(f"- Pool timeout: {db_config.get('pool_timeout', 'default')}s")
    print(f"- Pool recycle: {db_config.get('pool_recycle', 'default')}s")
    print(f"- SSL mode: {os.environ.get('DATABASE_SSL_MODE', 'require')}")
    
    return True


if __name__ == "__main__":
    # Load environment variables from .env.production if it exists
    env_path = Path(".env.production")
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print(f"Loaded environment from {env_path}")
    
    success = setup_production_database()
    sys.exit(0 if success else 1)
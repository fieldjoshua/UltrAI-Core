#!/usr/bin/env python3
"""
Initialize the UltraAI Core database.

This script runs Alembic migrations to create/update the database schema.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config
from app.database.session import get_database_url, check_db_connection
from app.utils.logging import get_logger

logger = get_logger(__name__)


def run_migrations():
    """Run Alembic migrations to initialize/update database."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    alembic_ini_path = project_root / "alembic.ini"
    
    if not alembic_ini_path.exists():
        logger.error(f"Alembic configuration not found at {alembic_ini_path}")
        return False
    
    try:
        # Create Alembic configuration
        alembic_cfg = Config(str(alembic_ini_path))
        
        # Set the database URL
        database_url = get_database_url()
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        logger.info(f"Running migrations for database: {database_url}")
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False


def create_initial_data():
    """Create initial data if needed."""
    from sqlalchemy.orm import Session
    from app.database.session import SessionLocal
    from app.database.models.user import User, UserRole, SubscriptionTier
    from app.services.auth_service_new import AuthService
    
    # Check if we should create demo user
    if os.getenv("CREATE_DEMO_USER", "false").lower() != "true":
        return
    
    auth_service = AuthService(
        jwt_secret=os.getenv("JWT_SECRET", "demo-secret")
    )
    
    db: Session = SessionLocal()
    try:
        # Check if demo user exists
        demo_user = db.query(User).filter(User.email == "demo@ultrai.app").first()
        if demo_user:
            logger.info("Demo user already exists")
            return
        
        # Create demo user
        demo_user = User(
            email="demo@ultrai.app",
            username="demo",
            full_name="Demo User",
            hashed_password=auth_service.hash_password("demo123"),
            role=UserRole.USER,
            subscription_tier=SubscriptionTier.FREE,
            account_balance=100.0,  # Start with $100 credit
            is_verified=True,
        )
        
        db.add(demo_user)
        db.commit()
        
        logger.info("Demo user created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create initial data: {str(e)}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main function to initialize database."""
    logger.info("Starting database initialization...")
    
    # Run migrations
    if not run_migrations():
        logger.error("Migration failed, exiting")
        sys.exit(1)
    
    # Check database connection
    if not check_db_connection():
        logger.error("Database connection check failed")
        sys.exit(1)
    
    # Create initial data
    create_initial_data()
    
    logger.info("Database initialization completed successfully")


if __name__ == "__main__":
    main()
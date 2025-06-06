"""
Database availability check utility.

This module provides a utility to wait for the database to be ready
before starting the application.
"""

import logging
import os
import sys
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
MAX_RETRIES = int(os.getenv("DB_CONNECTION_RETRIES", "30"))
RETRY_INTERVAL = int(os.getenv("DB_CONNECTION_RETRY_INTERVAL", "2"))


def main():
    """
    Wait for the database to be ready

    Returns:
        0 if database is ready, exits with 1 if max retries exceeded
    """
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)

    logger.info(f"Connecting to database: {DATABASE_URL.split('@')[-1]}")

    # Create engine without pooling connections
    engine = create_engine(DATABASE_URL, poolclass=None, pool_pre_ping=True)

    # Try to connect to the database
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Try to connect
            conn = engine.connect()
            conn.close()
            logger.info("Database connection successful!")
            return 0
        except OperationalError as e:
            retries += 1
            logger.warning(
                f"Database connection failed ({retries}/{MAX_RETRIES}): {str(e)}"
            )
            if retries >= MAX_RETRIES:
                logger.error("Max retries exceeded, giving up")
                sys.exit(1)
            time.sleep(RETRY_INTERVAL)

    # Should never reach here, but just in case
    logger.error("Failed to connect to database")
    sys.exit(1)


if __name__ == "__main__":
    main()

"""
Migration health check for the Ultra backend.

This module provides health check functions for database migrations.
"""

import os
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, Optional

from backend.utils.health_check import HealthStatus
from backend.utils.logging import get_logger

# Configure logging
logger = get_logger("migration_health", "logs/migration_health.log")

# Constants
ALEMBIC_CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), 'alembic.ini')


def get_migration_info() -> Dict[str, Any]:
    """
    Get information about the current migration status.

    Returns:
        Dictionary with migration status details
    """
    try:
        start_time = time.time()
        
        # Get current revision
        cmd = ['alembic', '-c', ALEMBIC_CONFIG, 'current', '--verbose']
        current_output = subprocess.check_output(cmd, universal_newlines=True)
        
        # Get migration history
        cmd = ['alembic', '-c', ALEMBIC_CONFIG, 'history', '--verbose']
        history_output = subprocess.check_output(cmd, universal_newlines=True)
        
        # Parse the outputs to extract information
        current_revision = None
        current_revision_date = None
        for line in current_output.splitlines():
            if "current revision" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    current_revision = parts[1].strip()
            if "Revision ID:" in line and current_revision in line:
                next_line_idx = current_output.splitlines().index(line) + 1
                if next_line_idx < len(current_output.splitlines()):
                    date_line = current_output.splitlines()[next_line_idx]
                    if "Create Date:" in date_line:
                        current_revision_date = date_line.split(":", 1)[1].strip()
        
        # Count total migrations from history
        migrations = [line for line in history_output.splitlines() if line.startswith("Rev: ")]
        total_migrations = len(migrations)
        
        # Parse pending migrations
        cmd = ['alembic', '-c', ALEMBIC_CONFIG, 'history', '--verbose', f"{current_revision or 'base'}:head"]
        pending_output = subprocess.check_output(cmd, universal_newlines=True)
        pending_lines = [line for line in pending_output.splitlines() if line.startswith("Rev: ")]
        pending_migrations = max(0, len(pending_lines) - 1)  # Subtract 1 for current
        
        # Get pending migration details
        pending_details = []
        if pending_migrations > 0:
            for line in pending_lines[1:]:  # Skip the current revision
                rev_id = line.split(" ")[1].strip(",")
                desc_idx = pending_output.splitlines().index(line) + 1
                if desc_idx < len(pending_output.splitlines()):
                    desc_line = pending_output.splitlines()[desc_idx]
                    if "Parent revision:" not in desc_line:
                        desc = desc_line.strip()
                        pending_details.append({"revision": rev_id, "description": desc})
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "current_revision": current_revision,
            "current_revision_date": current_revision_date,
            "total_migrations": total_migrations,
            "pending_migrations": pending_migrations,
            "pending_details": pending_details,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting migration info: {e.output.decode('utf-8') if hasattr(e, 'output') else str(e)}")
        return {
            "error": str(e),
            "duration_ms": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Unexpected error getting migration info: {str(e)}")
        return {
            "error": str(e),
            "duration_ms": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }


def check_migration_health() -> Dict[str, Any]:
    """
    Check database migration health.
    
    Returns:
        Health check result with migration status
    """
    try:
        start_time = time.time()
        
        # Get migration information
        migration_info = get_migration_info()
        
        # Check for errors in getting migration info
        if "error" in migration_info:
            return {
                "status": HealthStatus.UNAVAILABLE,
                "message": f"Failed to check migration status: {migration_info['error']}",
                "error": migration_info["error"],
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        # Check for pending migrations
        pending_migrations = migration_info.get("pending_migrations", 0)
        
        if pending_migrations > 0:
            # Migrations are pending - this is a degraded state
            return {
                "status": HealthStatus.DEGRADED,
                "message": f"{pending_migrations} pending database migrations need to be applied",
                "details": migration_info,
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        # No pending migrations - healthy state
        return {
            "status": HealthStatus.OK,
            "message": "Database schema is up to date",
            "details": migration_info,
            "duration_ms": int((time.time() - start_time) * 1000),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNAVAILABLE,
            "message": f"Migration health check failed: {str(e)}",
            "error": str(e),
            "duration_ms": int((time.time() - start_time) * 1000),
            "timestamp": datetime.utcnow().isoformat(),
        }


def register_migration_health_check():
    """
    Register the migration health check with the health check registry.
    """
    from backend.utils.health_check import HealthCheck, ServiceType, health_check_registry
    
    # Create migration health check
    migration_check = HealthCheck(
        name="database_migrations",
        service_type=ServiceType.DATABASE,
        check_fn=check_migration_health,
        description="Database migration status",
        is_critical=False,  # Pending migrations are degraded, not critical
        check_interval=300,  # Check every 5 minutes to reduce overhead
        dependent_services=["database"],
    )
    
    # Register with health check registry
    health_check_registry.register(migration_check)
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from alembic import command
from alembic.config import Config as AlembicConfig


def run_migrations():
    """Run database migrations."""
    # Get the path to the alembic.ini file
    alembic_ini_path = project_root / "alembic.ini"

    # Create Alembic configuration
    alembic_cfg = AlembicConfig(str(alembic_ini_path))

    # Run the migration
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run_migrations()

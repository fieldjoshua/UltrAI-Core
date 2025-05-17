"""Initial migration setup

Revision ID: 1eecfa604b93
Revises:
Create Date: 2025-05-02 13:25:59.274135

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1eecfa604b93"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema and/or data."""
    pass


def downgrade() -> None:
    """Downgrade database schema and/or data."""
    pass

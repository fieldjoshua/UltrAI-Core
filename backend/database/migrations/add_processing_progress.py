"""Add processing_progress to documents

Revision ID: add_processing_progress
Revises:
Create Date: 2024-03-19 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_processing_progress"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add processing_progress column to documents table
    op.add_column(
        "documents",
        sa.Column(
            "processing_progress", sa.Float(), nullable=False, server_default="0.0"
        ),
    )


def downgrade():
    # Remove processing_progress column from documents table
    op.drop_column("documents", "processing_progress")

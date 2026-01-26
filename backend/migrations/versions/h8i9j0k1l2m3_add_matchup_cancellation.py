"""Add matchup cancellation fields

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2_add_voting_feature
Create Date: 2026-01-26

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "h8i9j0k1l2m3"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "matchups",
        sa.Column("is_cancelled", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column("matchups", sa.Column("cancelled_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("matchups", "cancelled_at")
    op.drop_column("matchups", "is_cancelled")

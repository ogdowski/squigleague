"""add match army lists

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6a7
Create Date: 2025-01-21

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3d4e5f6g7h8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("player1_army_list", sa.Text(), nullable=True))
    op.add_column(
        "matches", sa.Column("player1_army_faction", sa.String(50), nullable=True)
    )
    op.add_column(
        "matches", sa.Column("player1_list_submitted_at", sa.DateTime(), nullable=True)
    )
    op.add_column("matches", sa.Column("player2_army_list", sa.Text(), nullable=True))
    op.add_column(
        "matches", sa.Column("player2_army_faction", sa.String(50), nullable=True)
    )
    op.add_column(
        "matches", sa.Column("player2_list_submitted_at", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "matches", sa.Column("lists_revealed_at", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("matches", "lists_revealed_at")
    op.drop_column("matches", "player2_list_submitted_at")
    op.drop_column("matches", "player2_army_faction")
    op.drop_column("matches", "player2_army_list")
    op.drop_column("matches", "player1_list_submitted_at")
    op.drop_column("matches", "player1_army_faction")
    op.drop_column("matches", "player1_army_list")

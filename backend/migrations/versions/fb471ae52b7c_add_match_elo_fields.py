"""add match elo fields

Revision ID: fb471ae52b7c
Revises: 86e3a9a35085
Create Date: 2026-01-19 13:20:41.714142

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fb471ae52b7c"
down_revision: Union[str, None] = "86e3a9a35085"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "matches", sa.Column("player1_elo_before", sa.Integer(), nullable=True)
    )
    op.add_column(
        "matches", sa.Column("player1_elo_after", sa.Integer(), nullable=True)
    )
    op.add_column(
        "matches", sa.Column("player2_elo_before", sa.Integer(), nullable=True)
    )
    op.add_column(
        "matches", sa.Column("player2_elo_after", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("matches", "player2_elo_after")
    op.drop_column("matches", "player2_elo_before")
    op.drop_column("matches", "player1_elo_after")
    op.drop_column("matches", "player1_elo_before")

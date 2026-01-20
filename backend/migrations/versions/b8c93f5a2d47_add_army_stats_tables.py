"""add_army_stats_tables

Revision ID: b8c93f5a2d47
Revises: a7d82e4f9c31
Create Date: 2026-01-20 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b8c93f5a2d47"
down_revision: Union[str, None] = "a7d82e4f9c31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create army_stats table
    op.create_table(
        "army_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("faction", sa.String(length=100), nullable=False),
        sa.Column("games_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("draws", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_army_stats_faction"), "army_stats", ["faction"], unique=True
    )

    # Create army_matchup_stats table
    op.create_table(
        "army_matchup_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("faction", sa.String(length=100), nullable=False),
        sa.Column("opponent_faction", sa.String(length=100), nullable=False),
        sa.Column("games_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("draws", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_army_matchup_stats_faction"),
        "army_matchup_stats",
        ["faction"],
        unique=False,
    )
    op.create_index(
        op.f("ix_army_matchup_stats_opponent_faction"),
        "army_matchup_stats",
        ["opponent_faction"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_army_matchup_stats_opponent_faction"), table_name="army_matchup_stats"
    )
    op.drop_index(
        op.f("ix_army_matchup_stats_faction"), table_name="army_matchup_stats"
    )
    op.drop_table("army_matchup_stats")
    op.drop_index(op.f("ix_army_stats_faction"), table_name="army_stats")
    op.drop_table("army_stats")

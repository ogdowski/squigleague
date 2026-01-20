"""add matchup result and army faction fields

Revision ID: b2c3d4e5f6a7
Revises: 5049268fdcd4
Create Date: 2026-01-20 14:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "b8c93f5a2d47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Optional title field
    op.add_column("matchups", sa.Column("title", sa.String(100), nullable=True))

    # Army faction fields for matchups
    op.add_column(
        "matchups", sa.Column("player1_army_faction", sa.String(50), nullable=True)
    )
    op.add_column(
        "matchups", sa.Column("player2_army_faction", sa.String(50), nullable=True)
    )

    # Game result fields
    op.add_column("matchups", sa.Column("player1_score", sa.Integer(), nullable=True))
    op.add_column("matchups", sa.Column("player2_score", sa.Integer(), nullable=True))

    # Result submission workflow fields
    op.add_column("matchups", sa.Column("result_status", sa.String(30), nullable=True))
    op.add_column(
        "matchups", sa.Column("result_submitted_by_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "matchups", sa.Column("result_submitted_at", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "matchups", sa.Column("result_confirmed_by_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "matchups", sa.Column("result_confirmed_at", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "matchups", sa.Column("result_auto_confirm_at", sa.DateTime(), nullable=True)
    )

    # Add foreign key constraints
    op.create_foreign_key(
        "fk_matchups_result_submitted_by",
        "matchups",
        "users",
        ["result_submitted_by_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_matchups_result_confirmed_by",
        "matchups",
        "users",
        ["result_confirmed_by_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_matchups_result_confirmed_by", "matchups", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_matchups_result_submitted_by", "matchups", type_="foreignkey"
    )

    op.drop_column("matchups", "result_auto_confirm_at")
    op.drop_column("matchups", "result_confirmed_at")
    op.drop_column("matchups", "result_confirmed_by_id")
    op.drop_column("matchups", "result_submitted_at")
    op.drop_column("matchups", "result_submitted_by_id")
    op.drop_column("matchups", "result_status")
    op.drop_column("matchups", "player2_score")
    op.drop_column("matchups", "player1_score")
    op.drop_column("matchups", "player2_army_faction")
    op.drop_column("matchups", "player1_army_faction")
    op.drop_column("matchups", "title")

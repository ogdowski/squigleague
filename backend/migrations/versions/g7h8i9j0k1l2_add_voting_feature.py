"""Add voting feature

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2026-01-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, None] = "f6g7h8i9j0k1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add voting fields to leagues table
    op.add_column(
        "leagues",
        sa.Column(
            "voting_enabled",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "leagues",
        sa.Column(
            "voting_closed_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # Create vote_categories table
    op.create_table(
        "vote_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("league_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("winner_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["league_id"], ["leagues.id"]),
        sa.ForeignKeyConstraint(["winner_id"], ["league_players.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_vote_categories_league_id"),
        "vote_categories",
        ["league_id"],
        unique=False,
    )

    # Create votes table
    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("voter_id", sa.Integer(), nullable=False),
        sa.Column("voted_for_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["vote_categories.id"]),
        sa.ForeignKeyConstraint(["voter_id"], ["league_players.id"]),
        sa.ForeignKeyConstraint(["voted_for_id"], ["league_players.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category_id", "voter_id", name="uq_vote_category_voter"),
    )
    op.create_index(
        op.f("ix_votes_category_id"),
        "votes",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_votes_voter_id"),
        "votes",
        ["voter_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_votes_voted_for_id"),
        "votes",
        ["voted_for_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop votes table
    op.drop_index(op.f("ix_votes_voted_for_id"), table_name="votes")
    op.drop_index(op.f("ix_votes_voter_id"), table_name="votes")
    op.drop_index(op.f("ix_votes_category_id"), table_name="votes")
    op.drop_table("votes")

    # Drop vote_categories table
    op.drop_index(op.f("ix_vote_categories_league_id"), table_name="vote_categories")
    op.drop_table("vote_categories")

    # Drop voting columns from leagues
    op.drop_column("leagues", "voting_closed_at")
    op.drop_column("leagues", "voting_enabled")

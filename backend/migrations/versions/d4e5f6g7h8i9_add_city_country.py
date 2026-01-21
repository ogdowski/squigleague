"""Add city and country fields

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-01-21
"""

import sqlalchemy as sa
from alembic import op

revision = "d4e5f6g7h8i9"
down_revision = "c3d4e5f6g7h8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add city and country to users
    op.add_column("users", sa.Column("city", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("country", sa.String(100), nullable=True))

    # Add city and country to leagues
    op.add_column("leagues", sa.Column("city", sa.String(100), nullable=True))
    op.add_column("leagues", sa.Column("country", sa.String(100), nullable=True))

    # Create locations table for autocomplete cache
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("city", sa.String(100), nullable=True, index=True),
        sa.Column("country", sa.String(100), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("locations")
    op.drop_column("users", "city")
    op.drop_column("users", "country")
    op.drop_column("leagues", "city")
    op.drop_column("leagues", "country")

"""Add points field to manifestation lores.

Universal manifestation lores (Morbid Conjuration, Primal Energy, etc.)
have a points cost associated with the lore group.

Revision ID: m3n4o5p6q7r8
Revises: l2m3n4o5p6q7
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "m3n4o5p6q7r8"
down_revision = "l2m3n4o5p6q7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    if "bsdata_manifestation_lores" not in inspector.get_table_names():
        return

    existing_columns = {
        col["name"] for col in inspector.get_columns("bsdata_manifestation_lores")
    }

    if "points" not in existing_columns:
        op.add_column(
            "bsdata_manifestation_lores",
            sa.Column("points", sa.Integer(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("bsdata_manifestation_lores", "points")

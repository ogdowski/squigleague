"""Add weapons and abilities JSON fields to manifestations.

Stores weapon profiles and ability profiles parsed from BSData
manifestation selection entries (e.g. Burning Head ranged attack).

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "l2m3n4o5p6q7"
down_revision = "k1l2m3n4o5p6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    if "bsdata_manifestations" not in inspector.get_table_names():
        return

    existing_columns = {
        col["name"] for col in inspector.get_columns("bsdata_manifestations")
    }

    if "weapons" not in existing_columns:
        op.add_column(
            "bsdata_manifestations",
            sa.Column("weapons", sa.Text(), nullable=True),
        )

    if "abilities" not in existing_columns:
        op.add_column(
            "bsdata_manifestations",
            sa.Column("abilities", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("bsdata_manifestations", "abilities")
    op.drop_column("bsdata_manifestations", "weapons")

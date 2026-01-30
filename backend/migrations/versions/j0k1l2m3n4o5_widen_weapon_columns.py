"""Widen weapon stat columns from varchar to text.

BSData contains long ability references like "See 'X' ability" in
hit/wound/rend/damage fields that exceed varchar(10/20) limits.

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "j0k1l2m3n4o5"
down_revision = "i9j0k1l2m3n4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    if "bsdata_weapons" not in inspector.get_table_names():
        return

    columns = {col["name"]: col for col in inspector.get_columns("bsdata_weapons")}

    for col_name in ("range", "attacks", "hit", "wound", "rend", "damage"):
        col_type = columns.get(col_name, {}).get("type")
        if col_type is not None and not isinstance(col_type, sa.Text):
            op.alter_column(
                "bsdata_weapons",
                col_name,
                type_=sa.Text(),
                existing_nullable=True,
            )


def downgrade() -> None:
    op.alter_column(
        "bsdata_weapons", "range", type_=sa.String(20), existing_nullable=True
    )
    op.alter_column(
        "bsdata_weapons", "attacks", type_=sa.String(20), existing_nullable=True
    )
    op.alter_column(
        "bsdata_weapons", "hit", type_=sa.String(10), existing_nullable=True
    )
    op.alter_column(
        "bsdata_weapons", "wound", type_=sa.String(10), existing_nullable=True
    )
    op.alter_column(
        "bsdata_weapons", "rend", type_=sa.String(10), existing_nullable=True
    )
    op.alter_column(
        "bsdata_weapons", "damage", type_=sa.String(20), existing_nullable=True
    )

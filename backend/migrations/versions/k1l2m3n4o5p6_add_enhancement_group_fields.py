"""Add group_name and is_seasonal to heroic_traits and artefacts.

Supports Scourge of Ghyran seasonal enhancement groups with
distinct group names (e.g. Great Endrinworks, Monstrous Traits).

Revision ID: k1l2m3n4o5p6
Revises: j0k1l2m3n4o5
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "k1l2m3n4o5p6"
down_revision = "j0k1l2m3n4o5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    for table_name in ("bsdata_heroic_traits", "bsdata_artefacts"):
        if table_name not in inspector.get_table_names():
            continue

        existing_columns = {col["name"] for col in inspector.get_columns(table_name)}

        if "group_name" not in existing_columns:
            op.add_column(
                table_name,
                sa.Column("group_name", sa.String(200), nullable=True),
            )

        if "is_seasonal" not in existing_columns:
            op.add_column(
                table_name,
                sa.Column(
                    "is_seasonal",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.text("false"),
                ),
            )


def downgrade() -> None:
    for table_name in ("bsdata_heroic_traits", "bsdata_artefacts"):
        op.drop_column(table_name, "is_seasonal")
        op.drop_column(table_name, "group_name")

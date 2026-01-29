"""Add bsdata_unit_factions junction table for many-to-many unit-faction.

Replaces duplicated AoR unit rows with lightweight junction links.

Revision ID: k1l2m3n4o5p6
Revises: j0k1l2m3n4o5
Create Date: 2026-01-29
"""

import sqlalchemy as sa
from alembic import op

revision = "k1l2m3n4o5p6"
down_revision = "j0k1l2m3n4o5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bsdata_unit_factions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("unit_id", sa.Integer(), nullable=False),
        sa.Column("faction_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["unit_id"], ["bsdata_units.id"]),
        sa.ForeignKeyConstraint(["faction_id"], ["bsdata_factions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_bsdata_unit_factions_unit_id"),
        "bsdata_unit_factions",
        ["unit_id"],
    )
    op.create_index(
        op.f("ix_bsdata_unit_factions_faction_id"),
        "bsdata_unit_factions",
        ["faction_id"],
    )


def downgrade():
    op.drop_index(
        op.f("ix_bsdata_unit_factions_faction_id"),
        table_name="bsdata_unit_factions",
    )
    op.drop_index(
        op.f("ix_bsdata_unit_factions_unit_id"),
        table_name="bsdata_unit_factions",
    )
    op.drop_table("bsdata_unit_factions")

"""Refactor: AoR as faction, prayer lores, core ability fields.

- Add is_aor and parent_faction_id to bsdata_factions
- Add timing/declare/color to bsdata_core_abilities
- Create bsdata_prayer_lores and bsdata_prayers tables
- Drop bsdata_aor_battle_traits and bsdata_armies_of_renown tables

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-01-29
"""

import sqlalchemy as sa
from alembic import op

revision = "j0k1l2m3n4o5"
down_revision = "i9j0k1l2m3n4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Faction: add is_aor flag and parent_faction_id
    op.add_column(
        "bsdata_factions",
        sa.Column("is_aor", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "bsdata_factions",
        sa.Column(
            "parent_faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            nullable=True,
        ),
    )

    # CoreAbility: add timing/declare/color (inherits AbilityBase now)
    op.add_column(
        "bsdata_core_abilities", sa.Column("timing", sa.Text(), nullable=True)
    )
    op.add_column(
        "bsdata_core_abilities", sa.Column("declare", sa.Text(), nullable=True)
    )
    op.add_column(
        "bsdata_core_abilities", sa.Column("color", sa.String(30), nullable=True)
    )

    # Prayer Lores table
    op.create_table(
        "bsdata_prayer_lores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "bsdata_id",
            sa.String(100),
            unique=True,
            index=True,
            nullable=False,
        ),
        sa.Column(
            "faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(200), index=True, nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
    )

    # Prayers table
    op.create_table(
        "bsdata_prayers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "bsdata_id",
            sa.String(100),
            unique=True,
            index=True,
            nullable=False,
        ),
        sa.Column(
            "lore_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_prayer_lores.id"),
            index=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("chanting_value", sa.String(10), nullable=True),
        sa.Column("range", sa.String(20), nullable=True),
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
    )

    # Drop old AoR tables
    op.drop_table("bsdata_aor_battle_traits")
    op.drop_table("bsdata_armies_of_renown")


def downgrade() -> None:
    # Recreate old AoR tables
    op.create_table(
        "bsdata_armies_of_renown",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "bsdata_id",
            sa.String(100),
            unique=True,
            index=True,
            nullable=False,
        ),
        sa.Column(
            "faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            index=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(200), index=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "bsdata_aor_battle_traits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "bsdata_id",
            sa.String(100),
            unique=True,
            index=True,
            nullable=False,
        ),
        sa.Column(
            "army_of_renown_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_armies_of_renown.id"),
            index=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("effect", sa.Text(), nullable=True),
    )

    # Drop new tables
    op.drop_table("bsdata_prayers")
    op.drop_table("bsdata_prayer_lores")

    # Remove core ability fields
    op.drop_column("bsdata_core_abilities", "color")
    op.drop_column("bsdata_core_abilities", "declare")
    op.drop_column("bsdata_core_abilities", "timing")

    # Remove faction fields
    op.drop_column("bsdata_factions", "parent_faction_id")
    op.drop_column("bsdata_factions", "is_aor")

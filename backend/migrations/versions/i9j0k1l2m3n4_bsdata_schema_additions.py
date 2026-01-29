"""BSData schema additions: battle profile fields, ability timing/color,
keywords, battle formations, and enhancement point costs.

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-01-29
"""

import sqlalchemy as sa
from alembic import op

revision = "i9j0k1l2m3n4"
down_revision = "h8i9j0k1l2m3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Unit battle profile fields
    op.add_column("bsdata_units", sa.Column("base_size", sa.Text(), nullable=True))
    op.add_column("bsdata_units", sa.Column("unit_size", sa.Integer(), nullable=True))
    op.add_column(
        "bsdata_units",
        sa.Column(
            "can_be_reinforced", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
    op.add_column("bsdata_units", sa.Column("notes", sa.Text(), nullable=True))

    # Unit ability timing/color
    op.add_column(
        "bsdata_unit_abilities", sa.Column("timing", sa.Text(), nullable=True)
    )
    op.add_column(
        "bsdata_unit_abilities", sa.Column("declare", sa.Text(), nullable=True)
    )
    op.add_column(
        "bsdata_unit_abilities", sa.Column("color", sa.String(30), nullable=True)
    )

    # Battle trait, heroic trait, artefact timing/color/keywords/points
    for table in ["bsdata_battle_traits", "bsdata_heroic_traits", "bsdata_artefacts"]:
        op.add_column(table, sa.Column("timing", sa.Text(), nullable=True))
        op.add_column(table, sa.Column("declare", sa.Text(), nullable=True))
        op.add_column(table, sa.Column("color", sa.String(30), nullable=True))
        op.add_column(table, sa.Column("keywords", sa.Text(), nullable=True))

    # Points for heroic traits and artefacts
    op.add_column(
        "bsdata_heroic_traits", sa.Column("points", sa.Integer(), nullable=True)
    )
    op.add_column("bsdata_artefacts", sa.Column("points", sa.Integer(), nullable=True))

    # Keywords for spells
    op.add_column("bsdata_spells", sa.Column("keywords", sa.Text(), nullable=True))

    # Points for spell lores
    op.add_column(
        "bsdata_spell_lores", sa.Column("points", sa.Integer(), nullable=True)
    )

    # Battle formations table
    op.create_table(
        "bsdata_battle_formations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            index=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("ability_name", sa.String(200), nullable=True),
        sa.Column("ability_type", sa.String(30), nullable=True),
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("timing", sa.Text(), nullable=True),
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("color", sa.String(30), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("bsdata_battle_formations")
    op.drop_column("bsdata_spell_lores", "points")
    op.drop_column("bsdata_spells", "keywords")
    op.drop_column("bsdata_artefacts", "points")
    op.drop_column("bsdata_heroic_traits", "points")

    for table in ["bsdata_artefacts", "bsdata_heroic_traits", "bsdata_battle_traits"]:
        op.drop_column(table, "keywords")
        op.drop_column(table, "color")
        op.drop_column(table, "declare")
        op.drop_column(table, "timing")

    op.drop_column("bsdata_unit_abilities", "color")
    op.drop_column("bsdata_unit_abilities", "declare")
    op.drop_column("bsdata_unit_abilities", "timing")
    op.drop_column("bsdata_units", "notes")
    op.drop_column("bsdata_units", "can_be_reinforced")
    op.drop_column("bsdata_units", "unit_size")
    op.drop_column("bsdata_units", "base_size")

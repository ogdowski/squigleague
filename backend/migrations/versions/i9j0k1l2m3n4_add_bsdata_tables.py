"""Add all BSData tables for Age of Sigmar rules browser.

Creates: grand_alliances, factions, units, weapons, unit_abilities,
battle_traits, battle_formations, heroic_traits, artefacts,
regiments_of_renown, ror_units, spell_lores, spells, prayer_lores,
prayers, manifestation_lores, manifestations, battle_tactic_cards,
core_abilities, unit_factions, sync_status.

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
    # Grand Alliances
    op.create_table(
        "bsdata_grand_alliances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), unique=True, index=True, nullable=False),
    )

    # Factions
    op.create_table(
        "bsdata_factions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(100), index=True, nullable=False),
        sa.Column(
            "grand_alliance_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_grand_alliances.id"),
            nullable=False,
        ),
        sa.Column("is_aor", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "parent_faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            nullable=True,
        ),
    )

    # Units
    op.create_table(
        "bsdata_units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            index=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(200), index=True, nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("move", sa.String(20), nullable=True),
        sa.Column("health", sa.Integer(), nullable=True),
        sa.Column("save", sa.String(10), nullable=True),
        sa.Column("control", sa.Integer(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("base_size", sa.Text(), nullable=True),
        sa.Column("unit_size", sa.Integer(), nullable=True),
        sa.Column(
            "can_be_reinforced", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # Unit-Faction junction (many-to-many for AoR)
    op.create_table(
        "bsdata_unit_factions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "unit_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_units.id"),
            nullable=False,
        ),
        sa.Column(
            "faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_bsdata_unit_factions_unit_id", "bsdata_unit_factions", ["unit_id"]
    )
    op.create_index(
        "ix_bsdata_unit_factions_faction_id", "bsdata_unit_factions", ["faction_id"]
    )

    # Weapons
    op.create_table(
        "bsdata_weapons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "unit_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_units.id"),
            index=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("weapon_type", sa.String(20), nullable=False),
        sa.Column("range", sa.String(20), nullable=True),
        sa.Column("attacks", sa.String(20), nullable=True),
        sa.Column("hit", sa.String(10), nullable=True),
        sa.Column("wound", sa.String(10), nullable=True),
        sa.Column("rend", sa.String(10), nullable=True),
        sa.Column("damage", sa.String(20), nullable=True),
        sa.Column("ability", sa.Text(), nullable=True),
    )

    # Unit Abilities
    op.create_table(
        "bsdata_unit_abilities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "unit_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_units.id"),
            index=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("ability_type", sa.String(30), nullable=False),
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("timing", sa.Text(), nullable=True),
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("color", sa.String(30), nullable=True),
    )

    # Battle Traits
    op.create_table(
        "bsdata_battle_traits",
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
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("timing", sa.Text(), nullable=True),
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("color", sa.String(30), nullable=True),
    )

    # Battle Formations
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
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("timing", sa.Text(), nullable=True),
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("color", sa.String(30), nullable=True),
    )

    # Heroic Traits
    op.create_table(
        "bsdata_heroic_traits",
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
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("timing", sa.Text(), nullable=True),
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("color", sa.String(30), nullable=True),
    )

    # Artefacts
    op.create_table(
        "bsdata_artefacts",
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
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("timing", sa.Text(), nullable=True),
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("color", sa.String(30), nullable=True),
    )

    # Regiments of Renown
    op.create_table(
        "bsdata_regiments_of_renown",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(200), index=True, nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("grand_alliances", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
    )

    # RoR Units
    op.create_table(
        "bsdata_ror_units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "regiment_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_regiments_of_renown.id"),
            index=True,
            nullable=False,
        ),
        sa.Column("unit_name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
    )

    # Spell Lores
    op.create_table(
        "bsdata_spell_lores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(200), index=True, nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
    )

    # Spells
    op.create_table(
        "bsdata_spells",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "lore_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_spell_lores.id"),
            index=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("casting_value", sa.String(10), nullable=True),
        sa.Column("range", sa.String(20), nullable=True),
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
    )

    # Prayer Lores
    op.create_table(
        "bsdata_prayer_lores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(200), index=True, nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
    )

    # Prayers
    op.create_table(
        "bsdata_prayers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
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
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
    )

    # Manifestation Lores
    op.create_table(
        "bsdata_manifestation_lores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "faction_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_factions.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(200), index=True, nullable=False),
    )

    # Manifestations
    op.create_table(
        "bsdata_manifestations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "lore_id",
            sa.Integer(),
            sa.ForeignKey("bsdata_manifestation_lores.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(200), index=True, nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("casting_value", sa.String(10), nullable=True),
        sa.Column("banishment", sa.String(10), nullable=True),
        sa.Column("move", sa.String(20), nullable=True),
        sa.Column("health", sa.Integer(), nullable=True),
        sa.Column("save", sa.String(10), nullable=True),
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
    )

    # Battle Tactic Cards
    op.create_table(
        "bsdata_battle_tactic_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(200), index=True, nullable=False),
        sa.Column("card_rules", sa.Text(), nullable=True),
        sa.Column("affray_name", sa.String(200), nullable=True),
        sa.Column("affray_effect", sa.Text(), nullable=True),
        sa.Column("strike_name", sa.String(200), nullable=True),
        sa.Column("strike_effect", sa.Text(), nullable=True),
        sa.Column("domination_name", sa.String(200), nullable=True),
        sa.Column("domination_effect", sa.Text(), nullable=True),
    )

    # Core Abilities
    op.create_table(
        "bsdata_core_abilities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bsdata_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(200), index=True, nullable=False),
        sa.Column("ability_type", sa.String(30), nullable=False),
        sa.Column("effect", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("timing", sa.Text(), nullable=True),
        sa.Column("declare", sa.Text(), nullable=True),
        sa.Column("color", sa.String(30), nullable=True),
    )

    # Sync Status
    op.create_table(
        "bsdata_sync_status",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("commit_hash", sa.String(40), nullable=False),
        sa.Column("commit_short", sa.String(7), nullable=False),
        sa.Column("synced_at", sa.DateTime(), nullable=False),
        sa.Column("factions_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("units_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sync_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="success"),
        sa.Column("error_message", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("bsdata_sync_status")
    op.drop_table("bsdata_core_abilities")
    op.drop_table("bsdata_battle_tactic_cards")
    op.drop_table("bsdata_manifestations")
    op.drop_table("bsdata_manifestation_lores")
    op.drop_table("bsdata_prayers")
    op.drop_table("bsdata_prayer_lores")
    op.drop_table("bsdata_spells")
    op.drop_table("bsdata_spell_lores")
    op.drop_table("bsdata_ror_units")
    op.drop_table("bsdata_regiments_of_renown")
    op.drop_table("bsdata_artefacts")
    op.drop_table("bsdata_heroic_traits")
    op.drop_table("bsdata_battle_formations")
    op.drop_table("bsdata_battle_traits")
    op.drop_table("bsdata_unit_abilities")
    op.drop_table("bsdata_weapons")
    op.drop_index(
        "ix_bsdata_unit_factions_faction_id", table_name="bsdata_unit_factions"
    )
    op.drop_index("ix_bsdata_unit_factions_unit_id", table_name="bsdata_unit_factions")
    op.drop_table("bsdata_unit_factions")
    op.drop_table("bsdata_units")
    op.drop_table("bsdata_factions")
    op.drop_table("bsdata_grand_alliances")

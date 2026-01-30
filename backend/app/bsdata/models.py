"""BSData models for Age of Sigmar 4th Edition game data."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

# =============================================================================
# Shared Base
# =============================================================================


class AbilityBase(SQLModel):
    """Shared ability fields used by traits, artefacts, formations, etc."""

    effect: Optional[str] = None
    keywords: Optional[str] = None  # JSON array
    timing: Optional[str] = None
    declare: Optional[str] = None
    color: Optional[str] = Field(default=None, max_length=30)


# =============================================================================
# Core Models
# =============================================================================


class GrandAlliance(SQLModel, table=True):
    """Grand Alliance (Order, Chaos, Death, Destruction)."""

    __tablename__ = "bsdata_grand_alliances"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=50)

    factions: list["Faction"] = Relationship(back_populates="grand_alliance")


class Faction(SQLModel, table=True):
    """Army faction (e.g., Stormcast Eternals, Ironjawz)."""

    __tablename__ = "bsdata_factions"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    name: str = Field(index=True, max_length=100)
    grand_alliance_id: int = Field(foreign_key="bsdata_grand_alliances.id")
    is_aor: bool = Field(default=False)
    parent_faction_id: Optional[int] = Field(
        default=None, foreign_key="bsdata_factions.id"
    )

    grand_alliance: GrandAlliance = Relationship(back_populates="factions")
    units: list["Unit"] = Relationship(back_populates="faction")
    battle_traits: list["BattleTrait"] = Relationship(back_populates="faction")
    battle_formations: list["BattleFormation"] = Relationship(back_populates="faction")
    heroic_traits: list["HeroicTrait"] = Relationship(back_populates="faction")
    artefacts: list["Artefact"] = Relationship(back_populates="faction")


# =============================================================================
# Unit Models
# =============================================================================


class UnitFaction(SQLModel, table=True):
    """Junction table linking units to additional factions (AoR)."""

    __tablename__ = "bsdata_unit_factions"

    id: Optional[int] = Field(default=None, primary_key=True)
    unit_id: int = Field(foreign_key="bsdata_units.id", index=True)
    faction_id: int = Field(foreign_key="bsdata_factions.id", index=True)


class Unit(SQLModel, table=True):
    """Unit with profile stats."""

    __tablename__ = "bsdata_units"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    faction_id: int = Field(foreign_key="bsdata_factions.id", index=True)
    name: str = Field(index=True, max_length=200)
    points: Optional[int] = None
    move: Optional[str] = Field(default=None, max_length=20)
    health: Optional[int] = None
    save: Optional[str] = Field(default=None, max_length=10)
    control: Optional[int] = None
    keywords: Optional[str] = None  # JSON array
    base_size: Optional[str] = None
    unit_size: Optional[int] = None
    can_be_reinforced: bool = Field(default=False)
    notes: Optional[str] = None

    faction: Faction = Relationship(back_populates="units")
    weapons: list["Weapon"] = Relationship(back_populates="unit")
    abilities: list["UnitAbility"] = Relationship(back_populates="unit")


class Weapon(SQLModel, table=True):
    """Weapon profile (ranged or melee)."""

    __tablename__ = "bsdata_weapons"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    unit_id: int = Field(foreign_key="bsdata_units.id", index=True)
    name: str = Field(max_length=200)
    weapon_type: str = Field(max_length=20)  # "ranged", "melee"
    range: Optional[str] = None
    attacks: Optional[str] = None
    hit: Optional[str] = None
    wound: Optional[str] = None
    rend: Optional[str] = None
    damage: Optional[str] = None
    ability: Optional[str] = None

    unit: Unit = Relationship(back_populates="weapons")


class UnitAbility(AbilityBase, table=True):
    """Unit ability (passive, activated, reaction)."""

    __tablename__ = "bsdata_unit_abilities"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    unit_id: int = Field(foreign_key="bsdata_units.id", index=True)
    name: str = Field(max_length=200)
    ability_type: str = Field(max_length=30)  # "passive", "activated", "spell", etc.

    unit: Unit = Relationship(back_populates="abilities")


# =============================================================================
# Faction Enhancements
# =============================================================================


class BattleTrait(AbilityBase, table=True):
    """Faction battle trait."""

    __tablename__ = "bsdata_battle_traits"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    faction_id: int = Field(foreign_key="bsdata_factions.id", index=True)
    name: str = Field(max_length=200)

    faction: Faction = Relationship(back_populates="battle_traits")


class BattleFormation(AbilityBase, table=True):
    """Battle Formation choice for a faction."""

    __tablename__ = "bsdata_battle_formations"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    faction_id: int = Field(foreign_key="bsdata_factions.id", index=True)
    name: str = Field(max_length=200)
    points: Optional[int] = None
    ability_name: Optional[str] = Field(default=None, max_length=200)
    ability_type: Optional[str] = Field(default=None, max_length=30)

    faction: Faction = Relationship(back_populates="battle_formations")


class HeroicTrait(AbilityBase, table=True):
    """Heroic trait for heroes."""

    __tablename__ = "bsdata_heroic_traits"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    faction_id: int = Field(foreign_key="bsdata_factions.id", index=True)
    name: str = Field(max_length=200)
    points: Optional[int] = None

    faction: Faction = Relationship(back_populates="heroic_traits")


class Artefact(AbilityBase, table=True):
    """Artefact of Power."""

    __tablename__ = "bsdata_artefacts"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    faction_id: int = Field(foreign_key="bsdata_factions.id", index=True)
    name: str = Field(max_length=200)
    points: Optional[int] = None

    faction: Faction = Relationship(back_populates="artefacts")


# =============================================================================
# Regiment of Renown
# =============================================================================


class RegimentOfRenown(SQLModel, table=True):
    """Regiment of Renown - mercenary regiment."""

    __tablename__ = "bsdata_regiments_of_renown"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    name: str = Field(index=True, max_length=200)
    points: Optional[int] = None
    grand_alliances: Optional[str] = None  # JSON array: ["Order", "Death"]
    description: Optional[str] = None

    units: list["RoRUnit"] = Relationship(back_populates="regiment")


class RoRUnit(SQLModel, table=True):
    """Unit included in a Regiment of Renown."""

    __tablename__ = "bsdata_ror_units"

    id: Optional[int] = Field(default=None, primary_key=True)
    regiment_id: int = Field(foreign_key="bsdata_regiments_of_renown.id", index=True)
    unit_name: str = Field(
        max_length=200
    )  # Name reference (may not exist in units table)
    quantity: int = Field(default=1)

    regiment: RegimentOfRenown = Relationship(back_populates="units")


# =============================================================================
# Spell Lores
# =============================================================================


class SpellLore(SQLModel, table=True):
    """Spell lore (e.g., Lore of Fire, Lore of Life)."""

    __tablename__ = "bsdata_spell_lores"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    faction_id: Optional[int] = Field(default=None, foreign_key="bsdata_factions.id")
    name: str = Field(index=True, max_length=200)
    points: Optional[int] = None

    spells: list["Spell"] = Relationship(back_populates="lore")


class Spell(SQLModel, table=True):
    """Individual spell."""

    __tablename__ = "bsdata_spells"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    lore_id: int = Field(foreign_key="bsdata_spell_lores.id", index=True)
    name: str = Field(max_length=200)
    casting_value: Optional[str] = Field(default=None, max_length=10)
    range: Optional[str] = Field(default=None, max_length=20)
    declare: Optional[str] = None
    effect: Optional[str] = None
    keywords: Optional[str] = None  # JSON array

    lore: SpellLore = Relationship(back_populates="spells")


# =============================================================================
# Prayer Lores
# =============================================================================


class PrayerLore(SQLModel, table=True):
    """Prayer lore (e.g., Lore of the Reclusians)."""

    __tablename__ = "bsdata_prayer_lores"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    faction_id: Optional[int] = Field(default=None, foreign_key="bsdata_factions.id")
    name: str = Field(index=True, max_length=200)
    points: Optional[int] = None

    prayers: list["Prayer"] = Relationship(back_populates="lore")


class Prayer(SQLModel, table=True):
    """Individual prayer."""

    __tablename__ = "bsdata_prayers"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    lore_id: int = Field(foreign_key="bsdata_prayer_lores.id", index=True)
    name: str = Field(max_length=200)
    chanting_value: Optional[str] = Field(default=None, max_length=10)
    range: Optional[str] = Field(default=None, max_length=20)
    declare: Optional[str] = None
    effect: Optional[str] = None
    keywords: Optional[str] = None  # JSON array

    lore: PrayerLore = Relationship(back_populates="prayers")


# =============================================================================
# Manifestations (Endless Spells, Invocations)
# =============================================================================


class ManifestationLore(SQLModel, table=True):
    """Manifestation lore (Endless Spells, Invocations)."""

    __tablename__ = "bsdata_manifestation_lores"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    faction_id: Optional[int] = Field(default=None, foreign_key="bsdata_factions.id")
    name: str = Field(index=True, max_length=200)

    manifestations: list["Manifestation"] = Relationship(back_populates="lore")


class Manifestation(SQLModel, table=True):
    """Individual manifestation (endless spell, invocation)."""

    __tablename__ = "bsdata_manifestations"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    lore_id: Optional[int] = Field(
        default=None, foreign_key="bsdata_manifestation_lores.id"
    )
    name: str = Field(index=True, max_length=200)
    points: Optional[int] = None
    casting_value: Optional[str] = Field(default=None, max_length=10)
    banishment: Optional[str] = Field(default=None, max_length=10)
    move: Optional[str] = Field(default=None, max_length=20)
    health: Optional[int] = None
    save: Optional[str] = Field(default=None, max_length=10)
    declare: Optional[str] = None
    effect: Optional[str] = None
    keywords: Optional[str] = None  # JSON array

    lore: Optional[ManifestationLore] = Relationship(back_populates="manifestations")


# =============================================================================
# GHB 2025-26 Content
# =============================================================================


class BattleTacticCard(SQLModel, table=True):
    """Battle Tactic Card from GHB 2025-26."""

    __tablename__ = "bsdata_battle_tactic_cards"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    name: str = Field(index=True, max_length=200)
    card_rules: Optional[str] = None
    affray_name: Optional[str] = Field(default=None, max_length=200)
    affray_effect: Optional[str] = None
    strike_name: Optional[str] = Field(default=None, max_length=200)
    strike_effect: Optional[str] = None
    domination_name: Optional[str] = Field(default=None, max_length=200)
    domination_effect: Optional[str] = None


class CoreAbility(AbilityBase, table=True):
    """Core game ability (Fly, Ward Save, etc.)."""

    __tablename__ = "bsdata_core_abilities"

    id: Optional[int] = Field(default=None, primary_key=True)
    bsdata_id: str = Field(unique=True, index=True, max_length=100)
    name: str = Field(index=True, max_length=200)
    ability_type: str = Field(max_length=30)  # "passive", "command", etc.


# =============================================================================
# Sync Metadata
# =============================================================================


class BSDataSyncStatus(SQLModel, table=True):
    """BSData sync status tracking."""

    __tablename__ = "bsdata_sync_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    commit_hash: str = Field(max_length=40)
    commit_short: str = Field(max_length=7)
    synced_at: datetime = Field(default_factory=datetime.utcnow)
    factions_count: int = Field(default=0)
    units_count: int = Field(default=0)
    sync_type: str = Field(max_length=20)  # "full", "incremental"
    status: str = Field(max_length=20, default="success")  # "success", "failed"
    error_message: Optional[str] = None

"""Pydantic schemas for BSData API."""

import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

# =============================================================================
# Shared Base
# =============================================================================


class KeywordsMixin(BaseModel):
    """Base schema with JSON keywords parsing."""

    keywords: Optional[list[str]] = None

    @field_validator("keywords", mode="before")
    @classmethod
    def parse_keywords_json(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return None
        return value


class AbilityResponseBase(KeywordsMixin):
    """Base schema for ability-like responses with timing/color fields."""

    effect: Optional[str] = None
    timing: Optional[str] = None
    declare: Optional[str] = None
    color: Optional[str] = None


# =============================================================================
# Grand Alliance & Faction
# =============================================================================


class GrandAllianceResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class FactionListItem(BaseModel):
    id: int
    name: str
    grand_alliance: str
    units_count: int = 0
    is_aor: bool = False
    parent_faction_id: Optional[int] = None

    class Config:
        from_attributes = True


class FactionDetail(BaseModel):
    id: int
    name: str
    bsdata_id: str
    grand_alliance: GrandAllianceResponse
    units_count: int = 0
    battle_traits_count: int = 0
    heroic_traits_count: int = 0
    artefacts_count: int = 0
    is_aor: bool = False
    parent_faction_id: Optional[int] = None

    class Config:
        from_attributes = True


# =============================================================================
# Unit
# =============================================================================


class WeaponResponse(BaseModel):
    id: int
    name: str
    weapon_type: str
    range: Optional[str] = None
    attacks: Optional[str] = None
    hit: Optional[str] = None
    wound: Optional[str] = None
    rend: Optional[str] = None
    damage: Optional[str] = None
    ability: Optional[str] = None

    class Config:
        from_attributes = True


class UnitAbilityResponse(AbilityResponseBase):
    id: int
    name: str
    ability_type: str

    class Config:
        from_attributes = True


class UnitListItem(KeywordsMixin):
    id: int
    name: str
    faction_name: str
    points: Optional[int] = None
    move: Optional[str] = None
    health: Optional[int] = None
    save: Optional[str] = None
    control: Optional[int] = None
    base_size: Optional[str] = None
    unit_size: Optional[int] = None
    can_be_reinforced: bool = False
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class UnitDetail(KeywordsMixin):
    id: int
    name: str
    bsdata_id: str
    faction_id: int
    faction_name: str
    points: Optional[int] = None
    move: Optional[str] = None
    health: Optional[int] = None
    save: Optional[str] = None
    control: Optional[int] = None
    base_size: Optional[str] = None
    unit_size: Optional[int] = None
    can_be_reinforced: bool = False
    notes: Optional[str] = None
    weapons: list[WeaponResponse] = []
    abilities: list[UnitAbilityResponse] = []

    class Config:
        from_attributes = True


# =============================================================================
# Battle Trait, Heroic Trait, Artefact
# =============================================================================


class BattleTraitResponse(AbilityResponseBase):
    id: int
    name: str

    class Config:
        from_attributes = True


class BattleFormationResponse(AbilityResponseBase):
    id: int
    name: str
    points: Optional[int] = None
    ability_name: Optional[str] = None
    ability_type: Optional[str] = None

    class Config:
        from_attributes = True


class HeroicTraitResponse(AbilityResponseBase):
    id: int
    name: str
    points: Optional[int] = None
    group_name: Optional[str] = None
    is_seasonal: bool = False

    class Config:
        from_attributes = True


class ArtefactResponse(AbilityResponseBase):
    id: int
    name: str
    points: Optional[int] = None
    group_name: Optional[str] = None
    is_seasonal: bool = False

    class Config:
        from_attributes = True


# =============================================================================
# Regiment of Renown
# =============================================================================


class RegimentOfRenownResponse(BaseModel):
    id: int
    name: str
    points: Optional[int] = None
    grand_alliances: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# Manifestation
# =============================================================================


class ManifestationResponse(BaseModel):
    id: int
    name: str
    points: Optional[int] = None
    casting_value: Optional[str] = None
    banishment: Optional[str] = None
    move: Optional[str] = None
    health: Optional[int] = None
    save: Optional[str] = None
    declare: Optional[str] = None
    effect: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# Spell Lore
# =============================================================================


class SpellResponse(KeywordsMixin):
    id: int
    name: str
    casting_value: Optional[str] = None
    range: Optional[str] = None
    declare: Optional[str] = None
    effect: Optional[str] = None

    class Config:
        from_attributes = True


class SpellLoreResponse(BaseModel):
    id: int
    name: str
    faction_id: Optional[int] = None
    points: Optional[int] = None
    spells: list[SpellResponse] = []

    class Config:
        from_attributes = True


# =============================================================================
# Battle Tactic Card
# =============================================================================


class BattleTacticCardResponse(BaseModel):
    id: int
    name: str
    card_rules: Optional[str] = None
    affray_name: Optional[str] = None
    affray_effect: Optional[str] = None
    strike_name: Optional[str] = None
    strike_effect: Optional[str] = None
    domination_name: Optional[str] = None
    domination_effect: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# Core Ability
# =============================================================================


class CoreAbilityResponse(AbilityResponseBase):
    id: int
    name: str
    ability_type: str

    class Config:
        from_attributes = True


# =============================================================================
# Sync Status
# =============================================================================


class SyncStatusResponse(BaseModel):
    commit: str
    commit_short: str
    last_sync: datetime
    factions_count: int
    units_count: int
    status: str

    class Config:
        from_attributes = True


class SyncResultResponse(BaseModel):
    sync_type: str
    commit: Optional[str] = None
    commit_short: Optional[str] = None
    factions_count: int = 0
    units_count: int = 0
    duration_seconds: Optional[float] = None
    message: Optional[str] = None
    error: Optional[str] = None
    status: Optional[str] = None


# =============================================================================
# Prayer Lore
# =============================================================================


class PrayerResponse(KeywordsMixin):
    id: int
    name: str
    chanting_value: Optional[str] = None
    range: Optional[str] = None
    declare: Optional[str] = None
    effect: Optional[str] = None

    class Config:
        from_attributes = True


class PrayerLoreResponse(BaseModel):
    id: int
    name: str
    faction_id: Optional[int] = None
    points: Optional[int] = None
    prayers: list[PrayerResponse] = []

    class Config:
        from_attributes = True


# =============================================================================
# Manifestation Lore
# =============================================================================


class ManifestationLoreResponse(BaseModel):
    id: int
    name: str
    faction_id: Optional[int] = None
    manifestations: list[ManifestationResponse] = []

    class Config:
        from_attributes = True


# =============================================================================
# Regiment of Renown (with units)
# =============================================================================


class RoRUnitResponse(BaseModel):
    id: int
    unit_name: str
    quantity: int = 1

    class Config:
        from_attributes = True


class RegimentOfRenownWithUnits(BaseModel):
    id: int
    name: str
    points: Optional[int] = None
    grand_alliances: Optional[str] = None
    description: Optional[str] = None
    units: list[RoRUnitResponse] = []

    class Config:
        from_attributes = True


# =============================================================================
# Faction Full (all data)
# =============================================================================


class FactionFull(BaseModel):
    id: int
    name: str
    grand_alliance_name: str
    is_aor: bool = False
    parent_faction_id: Optional[int] = None
    battle_traits: list[BattleTraitResponse] = []
    battle_formations: list[BattleFormationResponse] = []
    heroic_traits: list[HeroicTraitResponse] = []
    artefacts: list[ArtefactResponse] = []
    units: list[UnitListItem] = []
    spell_lores: list[SpellLoreResponse] = []
    prayer_lores: list[PrayerLoreResponse] = []
    manifestation_lores: list[ManifestationLoreResponse] = []
    regiments_of_renown: list[RegimentOfRenownWithUnits] = []

    class Config:
        from_attributes = True


# =============================================================================
# Search
# =============================================================================


class SearchResultItem(BaseModel):
    result_type: str  # "unit", "ability", "battle_trait", "heroic_trait", "artefact", "spell", "prayer"
    name: str
    faction_name: Optional[str] = None
    faction_id: Optional[int] = None
    unit_id: Optional[int] = None
    points: Optional[int] = None
    extra: Optional[str] = None  # e.g. ability type, phase

"""Pydantic schemas for BSData API."""

import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

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


class UnitAbilityResponse(BaseModel):
    id: int
    name: str
    ability_type: str
    effect: Optional[str] = None
    keywords: Optional[list[str]] = None
    timing: Optional[str] = None
    declare: Optional[str] = None
    color: Optional[str] = None

    @field_validator("keywords", mode="before")
    @classmethod
    def parse_keywords_json(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return None
        return value

    class Config:
        from_attributes = True


class UnitListItem(BaseModel):
    id: int
    name: str
    faction_name: str
    points: Optional[int] = None
    move: Optional[str] = None
    health: Optional[int] = None
    save: Optional[str] = None
    control: Optional[int] = None
    keywords: Optional[list[str]] = None
    base_size: Optional[str] = None
    unit_size: Optional[int] = None
    can_be_reinforced: bool = False
    notes: Optional[str] = None

    @field_validator("keywords", mode="before")
    @classmethod
    def parse_keywords_json(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return None
        return value

    class Config:
        from_attributes = True


class UnitDetail(BaseModel):
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
    keywords: Optional[list[str]] = None
    base_size: Optional[str] = None
    unit_size: Optional[int] = None
    can_be_reinforced: bool = False
    notes: Optional[str] = None
    weapons: list[WeaponResponse] = []
    abilities: list[UnitAbilityResponse] = []

    @field_validator("keywords", mode="before")
    @classmethod
    def parse_keywords_json(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return None
        return value

    class Config:
        from_attributes = True


# =============================================================================
# Battle Trait, Heroic Trait, Artefact
# =============================================================================


class BattleTraitResponse(BaseModel):
    id: int
    name: str
    effect: Optional[str] = None

    class Config:
        from_attributes = True


class HeroicTraitResponse(BaseModel):
    id: int
    name: str
    effect: Optional[str] = None

    class Config:
        from_attributes = True


class ArtefactResponse(BaseModel):
    id: int
    name: str
    effect: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# Army of Renown
# =============================================================================


class ArmyOfRenownListItem(BaseModel):
    id: int
    name: str
    faction_name: str

    class Config:
        from_attributes = True


class ArmyOfRenownDetail(BaseModel):
    id: int
    name: str
    bsdata_id: str
    faction_id: int
    faction_name: str
    description: Optional[str] = None

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
    effect: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# Spell Lore
# =============================================================================


class SpellResponse(BaseModel):
    id: int
    name: str
    casting_value: Optional[str] = None
    range: Optional[str] = None
    effect: Optional[str] = None

    class Config:
        from_attributes = True


class SpellLoreResponse(BaseModel):
    id: int
    name: str
    faction_id: Optional[int] = None
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


class CoreAbilityResponse(BaseModel):
    id: int
    name: str
    ability_type: str
    effect: Optional[str] = None

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
# Army of Renown (with battle traits)
# =============================================================================


class AoRBattleTraitResponse(BaseModel):
    id: int
    name: str
    effect: Optional[str] = None

    class Config:
        from_attributes = True


class ArmyOfRenownWithTraits(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    battle_traits: list[AoRBattleTraitResponse] = []

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
    battle_traits: list[BattleTraitResponse] = []
    heroic_traits: list[HeroicTraitResponse] = []
    artefacts: list[ArtefactResponse] = []
    units: list[UnitListItem] = []
    spell_lores: list[SpellLoreResponse] = []
    manifestation_lores: list[ManifestationLoreResponse] = []
    armies_of_renown: list[ArmyOfRenownWithTraits] = []
    regiments_of_renown: list[RegimentOfRenownWithUnits] = []

    class Config:
        from_attributes = True

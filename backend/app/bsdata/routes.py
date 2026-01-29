"""BSData API routes."""

from typing import Optional

from app.bsdata.models import (
    AoRBattleTrait,
    ArmyOfRenown,
    Artefact,
    BattleTacticCard,
    BattleTrait,
    BSDataSyncStatus,
    CoreAbility,
    Faction,
    GrandAlliance,
    HeroicTrait,
    Manifestation,
    ManifestationLore,
    RegimentOfRenown,
    RoRUnit,
    Spell,
    SpellLore,
    Unit,
    UnitAbility,
    Weapon,
)
from app.bsdata.schemas import (
    AoRBattleTraitResponse,
    ArmyOfRenownDetail,
    ArmyOfRenownListItem,
    ArmyOfRenownWithTraits,
    ArtefactResponse,
    BattleTacticCardResponse,
    BattleTraitResponse,
    CoreAbilityResponse,
    FactionDetail,
    FactionFull,
    FactionListItem,
    GrandAllianceResponse,
    HeroicTraitResponse,
    ManifestationLoreResponse,
    ManifestationResponse,
    RegimentOfRenownResponse,
    RegimentOfRenownWithUnits,
    RoRUnitResponse,
    SpellLoreResponse,
    SpellResponse,
    SyncResultResponse,
    SyncStatusResponse,
    UnitAbilityResponse,
    UnitDetail,
    UnitListItem,
    WeaponResponse,
)
from app.bsdata.sync import BSDataSync
from app.core.deps import get_current_user
from app.db import get_session
from app.users.models import User
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select

router = APIRouter(prefix="/bsdata", tags=["bsdata"])


@router.get("/grand-alliances", response_model=list[GrandAllianceResponse])
async def list_grand_alliances(session: Session = Depends(get_session)):
    """List all grand alliances."""
    alliances = session.exec(select(GrandAlliance)).all()
    return alliances


@router.get("/factions", response_model=list[FactionListItem])
async def list_factions(
    grand_alliance: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """List all factions with unit counts."""
    query = (
        select(
            Faction.id,
            Faction.name,
            GrandAlliance.name.label("grand_alliance"),
            func.count(Unit.id).label("units_count"),
        )
        .join(GrandAlliance)
        .outerjoin(Unit)
        .group_by(Faction.id, GrandAlliance.name)
        .order_by(GrandAlliance.name, Faction.name)
    )

    if grand_alliance:
        query = query.where(GrandAlliance.name == grand_alliance)

    results = session.exec(query).all()

    return [
        FactionListItem(
            id=row.id,
            name=row.name,
            grand_alliance=row.grand_alliance,
            units_count=row.units_count or 0,
        )
        for row in results
    ]


@router.get("/factions/{faction_id}", response_model=FactionDetail)
async def get_faction(faction_id: int, session: Session = Depends(get_session)):
    """Get faction details with counts."""
    faction = session.get(Faction, faction_id)
    if not faction:
        raise HTTPException(status_code=404, detail="Faction not found")

    units_count = session.exec(
        select(func.count(Unit.id)).where(Unit.faction_id == faction_id)
    ).one()

    battle_traits_count = session.exec(
        select(func.count(BattleTrait.id)).where(BattleTrait.faction_id == faction_id)
    ).one()

    heroic_traits_count = session.exec(
        select(func.count(HeroicTrait.id)).where(HeroicTrait.faction_id == faction_id)
    ).one()

    artefacts_count = session.exec(
        select(func.count(Artefact.id)).where(Artefact.faction_id == faction_id)
    ).one()

    return FactionDetail(
        id=faction.id,
        name=faction.name,
        bsdata_id=faction.bsdata_id,
        grand_alliance=GrandAllianceResponse(
            id=faction.grand_alliance.id,
            name=faction.grand_alliance.name,
        ),
        units_count=units_count,
        battle_traits_count=battle_traits_count,
        heroic_traits_count=heroic_traits_count,
        artefacts_count=artefacts_count,
    )


@router.get("/factions/{faction_id}/units", response_model=list[UnitListItem])
async def list_faction_units(
    faction_id: int,
    session: Session = Depends(get_session),
):
    """List all units in a faction."""
    faction = session.get(Faction, faction_id)
    if not faction:
        raise HTTPException(status_code=404, detail="Faction not found")

    units = session.exec(
        select(Unit).where(Unit.faction_id == faction_id).order_by(Unit.name)
    ).all()

    return [
        UnitListItem(
            id=unit.id,
            name=unit.name,
            faction_name=faction.name,
            points=unit.points,
            move=unit.move,
            health=unit.health,
            save=unit.save,
            control=unit.control,
            keywords=unit.keywords,
            base_size=unit.base_size,
            unit_size=unit.unit_size,
            can_be_reinforced=unit.can_be_reinforced,
            notes=unit.notes,
        )
        for unit in units
    ]


@router.get(
    "/factions/{faction_id}/battle-traits", response_model=list[BattleTraitResponse]
)
async def list_faction_battle_traits(
    faction_id: int,
    session: Session = Depends(get_session),
):
    """List battle traits for a faction."""
    traits = session.exec(
        select(BattleTrait)
        .where(BattleTrait.faction_id == faction_id)
        .order_by(BattleTrait.name)
    ).all()
    return traits


@router.get(
    "/factions/{faction_id}/heroic-traits", response_model=list[HeroicTraitResponse]
)
async def list_faction_heroic_traits(
    faction_id: int,
    session: Session = Depends(get_session),
):
    """List heroic traits for a faction."""
    traits = session.exec(
        select(HeroicTrait)
        .where(HeroicTrait.faction_id == faction_id)
        .order_by(HeroicTrait.name)
    ).all()
    return traits


@router.get("/factions/{faction_id}/artefacts", response_model=list[ArtefactResponse])
async def list_faction_artefacts(
    faction_id: int,
    session: Session = Depends(get_session),
):
    """List artefacts for a faction."""
    artefacts = session.exec(
        select(Artefact)
        .where(Artefact.faction_id == faction_id)
        .order_by(Artefact.name)
    ).all()
    return artefacts


@router.get(
    "/factions/{faction_id}/spell-lores", response_model=list[SpellLoreResponse]
)
async def list_faction_spell_lores(
    faction_id: int,
    session: Session = Depends(get_session),
):
    """List spell lores for a faction."""
    lores = session.exec(
        select(SpellLore)
        .where(SpellLore.faction_id == faction_id)
        .order_by(SpellLore.name)
    ).all()

    result = []
    for lore in lores:
        spells = session.exec(
            select(Spell).where(Spell.lore_id == lore.id).order_by(Spell.name)
        ).all()
        result.append(
            SpellLoreResponse(
                id=lore.id,
                name=lore.name,
                faction_id=lore.faction_id,
                spells=spells,
            )
        )
    return result


@router.get(
    "/factions/{faction_id}/manifestation-lores",
    response_model=list[ManifestationLoreResponse],
)
async def list_faction_manifestation_lores(
    faction_id: int,
    session: Session = Depends(get_session),
):
    """List manifestation lores for a faction."""
    lores = session.exec(
        select(ManifestationLore)
        .where(ManifestationLore.faction_id == faction_id)
        .order_by(ManifestationLore.name)
    ).all()

    result = []
    for lore in lores:
        manifestations = session.exec(
            select(Manifestation)
            .where(Manifestation.lore_id == lore.id)
            .order_by(Manifestation.name)
        ).all()
        result.append(
            ManifestationLoreResponse(
                id=lore.id,
                name=lore.name,
                faction_id=lore.faction_id,
                manifestations=[
                    ManifestationResponse.model_validate(m) for m in manifestations
                ],
            )
        )
    return result


@router.get(
    "/factions/{faction_id}/armies-of-renown",
    response_model=list[ArmyOfRenownWithTraits],
)
async def list_faction_armies_of_renown(
    faction_id: int,
    session: Session = Depends(get_session),
):
    """List armies of renown for a faction."""
    armies = session.exec(
        select(ArmyOfRenown)
        .where(ArmyOfRenown.faction_id == faction_id)
        .order_by(ArmyOfRenown.name)
    ).all()

    result = []
    for aor in armies:
        traits = session.exec(
            select(AoRBattleTrait).where(AoRBattleTrait.army_of_renown_id == aor.id)
        ).all()
        result.append(
            ArmyOfRenownWithTraits(
                id=aor.id,
                name=aor.name,
                description=aor.description,
                battle_traits=[
                    AoRBattleTraitResponse.model_validate(t) for t in traits
                ],
            )
        )
    return result


@router.get("/manifestation-lores", response_model=list[ManifestationLoreResponse])
async def list_manifestation_lores(session: Session = Depends(get_session)):
    """List universal manifestation lores (not faction-specific)."""
    lores = session.exec(
        select(ManifestationLore)
        .where(ManifestationLore.faction_id == None)
        .order_by(ManifestationLore.name)
    ).all()

    result = []
    for lore in lores:
        manifestations = session.exec(
            select(Manifestation)
            .where(Manifestation.lore_id == lore.id)
            .order_by(Manifestation.name)
        ).all()
        result.append(
            ManifestationLoreResponse(
                id=lore.id,
                name=lore.name,
                faction_id=lore.faction_id,
                manifestations=[
                    ManifestationResponse.model_validate(m) for m in manifestations
                ],
            )
        )

    # Include orphan manifestations
    orphans = session.exec(
        select(Manifestation)
        .where(Manifestation.lore_id == None)
        .order_by(Manifestation.name)
    ).all()
    if orphans:
        result.append(
            ManifestationLoreResponse(
                id=0,
                name="Endless Spells & Invocations",
                faction_id=None,
                manifestations=[
                    ManifestationResponse.model_validate(m) for m in orphans
                ],
            )
        )

    return result


@router.get("/units", response_model=list[UnitListItem])
async def list_units(
    search: Optional[str] = None,
    faction_id: Optional[int] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    session: Session = Depends(get_session),
):
    """List units with optional search and filtering."""
    query = select(Unit, Faction.name.label("faction_name")).join(Faction)

    if search:
        query = query.where(Unit.name.ilike(f"%{search}%"))

    if faction_id:
        query = query.where(Unit.faction_id == faction_id)

    query = query.order_by(Unit.name).offset(offset).limit(limit)
    results = session.exec(query).all()

    return [
        UnitListItem(
            id=unit.id,
            name=unit.name,
            faction_name=faction_name,
            points=unit.points,
            move=unit.move,
            health=unit.health,
            save=unit.save,
            control=unit.control,
            keywords=unit.keywords,
            base_size=unit.base_size,
            unit_size=unit.unit_size,
            can_be_reinforced=unit.can_be_reinforced,
            notes=unit.notes,
        )
        for unit, faction_name in results
    ]


@router.get("/units/{unit_id}", response_model=UnitDetail)
async def get_unit(unit_id: int, session: Session = Depends(get_session)):
    """Get unit details with weapons and abilities."""
    unit = session.get(Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    weapons = session.exec(select(Weapon).where(Weapon.unit_id == unit_id)).all()

    abilities = session.exec(
        select(UnitAbility).where(UnitAbility.unit_id == unit_id)
    ).all()

    return UnitDetail(
        id=unit.id,
        name=unit.name,
        bsdata_id=unit.bsdata_id,
        faction_id=unit.faction_id,
        faction_name=unit.faction.name,
        points=unit.points,
        move=unit.move,
        health=unit.health,
        save=unit.save,
        control=unit.control,
        keywords=unit.keywords,
        base_size=unit.base_size,
        unit_size=unit.unit_size,
        can_be_reinforced=unit.can_be_reinforced,
        notes=unit.notes,
        weapons=[WeaponResponse.model_validate(weapon) for weapon in weapons],
        abilities=[
            UnitAbilityResponse.model_validate(ability) for ability in abilities
        ],
    )


@router.get("/search/units", response_model=list[UnitListItem])
async def search_units(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, le=100),
    session: Session = Depends(get_session),
):
    """Search units by name."""
    query = (
        select(Unit, Faction.name.label("faction_name"))
        .join(Faction)
        .where(Unit.name.ilike(f"%{q}%"))
        .order_by(Unit.name)
        .limit(limit)
    )
    results = session.exec(query).all()

    return [
        UnitListItem(
            id=unit.id,
            name=unit.name,
            faction_name=faction_name,
            points=unit.points,
            move=unit.move,
            health=unit.health,
            save=unit.save,
            control=unit.control,
            keywords=unit.keywords,
            base_size=unit.base_size,
            unit_size=unit.unit_size,
            can_be_reinforced=unit.can_be_reinforced,
            notes=unit.notes,
        )
        for unit, faction_name in results
    ]


@router.get("/armies-of-renown", response_model=list[ArmyOfRenownListItem])
async def list_armies_of_renown(session: Session = Depends(get_session)):
    """List all Armies of Renown."""
    query = (
        select(ArmyOfRenown, Faction.name.label("faction_name"))
        .join(Faction)
        .order_by(Faction.name, ArmyOfRenown.name)
    )
    results = session.exec(query).all()

    return [
        ArmyOfRenownListItem(
            id=aor.id,
            name=aor.name,
            faction_name=faction_name,
        )
        for aor, faction_name in results
    ]


@router.get("/armies-of-renown/{aor_id}", response_model=ArmyOfRenownDetail)
async def get_army_of_renown(aor_id: int, session: Session = Depends(get_session)):
    """Get Army of Renown details."""
    aor = session.get(ArmyOfRenown, aor_id)
    if not aor:
        raise HTTPException(status_code=404, detail="Army of Renown not found")

    return ArmyOfRenownDetail(
        id=aor.id,
        name=aor.name,
        bsdata_id=aor.bsdata_id,
        faction_id=aor.faction_id,
        faction_name=aor.faction.name,
        description=aor.description,
    )


@router.get("/regiments-of-renown", response_model=list[RegimentOfRenownResponse])
async def list_regiments_of_renown(session: Session = Depends(get_session)):
    """List all Regiments of Renown."""
    regiments = session.exec(
        select(RegimentOfRenown).order_by(RegimentOfRenown.name)
    ).all()
    return regiments


@router.get("/manifestations", response_model=list[ManifestationResponse])
async def list_manifestations(session: Session = Depends(get_session)):
    """List all manifestations (endless spells, invocations)."""
    manifestations = session.exec(
        select(Manifestation).order_by(Manifestation.name)
    ).all()
    return manifestations


@router.get("/spell-lores", response_model=list[SpellLoreResponse])
async def list_spell_lores(session: Session = Depends(get_session)):
    """List all spell lores with their spells."""
    lores = session.exec(select(SpellLore).order_by(SpellLore.name)).all()

    result = []
    for lore in lores:
        spells = session.exec(
            select(Spell).where(Spell.lore_id == lore.id).order_by(Spell.name)
        ).all()
        result.append(
            SpellLoreResponse(
                id=lore.id,
                name=lore.name,
                faction_id=lore.faction_id,
                spells=spells,
            )
        )

    return result


@router.get("/battle-tactics", response_model=list[BattleTacticCardResponse])
async def list_battle_tactics(session: Session = Depends(get_session)):
    """List all battle tactic cards."""
    cards = session.exec(select(BattleTacticCard).order_by(BattleTacticCard.name)).all()
    return cards


@router.get("/core-abilities", response_model=list[CoreAbilityResponse])
async def list_core_abilities(session: Session = Depends(get_session)):
    """List all core abilities."""
    abilities = session.exec(select(CoreAbility).order_by(CoreAbility.name)).all()
    return abilities


@router.get("/status", response_model=Optional[SyncStatusResponse])
async def get_sync_status(session: Session = Depends(get_session)):
    """Get current BSData sync status."""
    status = session.exec(
        select(BSDataSyncStatus)
        .where(BSDataSyncStatus.status == "success")
        .order_by(BSDataSyncStatus.synced_at.desc())
    ).first()

    if not status:
        return None

    return SyncStatusResponse(
        commit=status.commit_hash,
        commit_short=status.commit_short,
        last_sync=status.synced_at,
        factions_count=status.factions_count,
        units_count=status.units_count,
        status=status.status,
    )


@router.post("/sync", response_model=SyncResultResponse)
async def trigger_sync(
    force_full: bool = False,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Trigger BSData sync (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    sync_service = BSDataSync(session)
    result = sync_service.sync(force_full=force_full)

    return SyncResultResponse(**result)

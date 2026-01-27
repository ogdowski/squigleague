"""BSData synchronization service using GitHub API (no git required)."""

import io
import logging
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
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
from app.bsdata.parser import BSDataParser, get_grand_alliance
from sqlmodel import Session, select

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/repos/BSData/age-of-sigmar-4th"
GITHUB_TARBALL_URL = (
    "https://github.com/BSData/age-of-sigmar-4th/archive/refs/heads/main.tar.gz"
)
BSDATA_LOCAL_PATH = Path("/app/bsdata/age-of-sigmar-4th")


class BSDataSync:
    """Service for syncing BSData to database via GitHub API."""

    def __init__(self, session: Session):
        self.session = session
        self.repo_path = BSDATA_LOCAL_PATH
        self.parser: Optional[BSDataParser] = None
        self._grand_alliance_cache: dict[str, int] = {}
        self._faction_cache: dict[str, int] = {}

    def get_current_commit(self) -> Optional[str]:
        """Get current BSData commit from database."""
        status = self.session.exec(
            select(BSDataSyncStatus)
            .where(BSDataSyncStatus.status == "success")
            .order_by(BSDataSyncStatus.synced_at.desc())
        ).first()
        return status.commit_hash if status else None

    def _get_latest_commit(self) -> str:
        """Get latest commit SHA from GitHub API."""
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{GITHUB_API_URL}/commits/main")
            response.raise_for_status()
            data = response.json()
            return data["sha"]

    def _download_and_extract(self) -> str:
        """Download tarball from GitHub and extract .cat/.gst files."""
        logger.info("Downloading BSData from GitHub...")

        # Create directory
        self.repo_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove old data if exists
        if self.repo_path.exists():
            import shutil

            shutil.rmtree(self.repo_path)

        # Download tarball
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            response = client.get(GITHUB_TARBALL_URL)
            response.raise_for_status()

            # Extract tarball
            with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar:
                # Find the root directory name (usually "age-of-sigmar-4th-main")
                root_dir = None
                for member in tar.getmembers():
                    if member.isdir() and "/" not in member.name:
                        root_dir = member.name
                        break

                # Extract only .cat and .gst files
                for member in tar.getmembers():
                    if member.name.endswith(".cat") or member.name.endswith(".gst"):
                        # Strip the root directory from the path
                        if root_dir and member.name.startswith(root_dir + "/"):
                            member.name = member.name[len(root_dir) + 1 :]

                        # Extract to our target directory
                        target_path = self.repo_path / member.name
                        target_path.parent.mkdir(parents=True, exist_ok=True)

                        # Extract file content
                        file_obj = tar.extractfile(member)
                        if file_obj:
                            target_path.write_bytes(file_obj.read())

        logger.info(f"Extracted BSData to {self.repo_path}")
        return self._get_latest_commit()

    def sync(self, force_full: bool = False) -> dict:
        """Main sync method. Returns stats dict."""
        start_time = datetime.utcnow()
        stats = {
            "sync_type": "full" if force_full else "incremental",
            "factions_count": 0,
            "units_count": 0,
            "started_at": start_time.isoformat(),
        }

        try:
            # Get latest commit from GitHub
            latest_commit = self._get_latest_commit()
            current_commit = self.get_current_commit()

            # Check if we need to sync
            if (
                not force_full
                and current_commit == latest_commit
                and self.repo_path.exists()
            ):
                stats["message"] = "No changes"
                stats["commit"] = latest_commit
                stats["commit_short"] = latest_commit[:7]
                return stats

            # Download and extract
            new_commit = self._download_and_extract()

            # Full sync always (incremental would require git diff which we don't have)
            stats["sync_type"] = "full"
            self.parser = BSDataParser(self.repo_path)
            sync_stats = self._full_sync()

            stats.update(sync_stats)
            stats["commit"] = new_commit
            stats["commit_short"] = new_commit[:7]

            # Save sync status
            sync_status = BSDataSyncStatus(
                commit_hash=new_commit,
                commit_short=new_commit[:7],
                synced_at=datetime.utcnow(),
                factions_count=stats.get("factions_count", 0),
                units_count=stats.get("units_count", 0),
                sync_type=stats["sync_type"],
                status="success",
            )
            self.session.add(sync_status)
            self.session.commit()

            stats["duration_seconds"] = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Sync completed: {stats}")

        except Exception as error:
            logger.exception("Sync failed")
            stats["status"] = "failed"
            stats["error"] = str(error)

            # Save failed sync status
            sync_status = BSDataSyncStatus(
                commit_hash="",
                commit_short="",
                synced_at=datetime.utcnow(),
                sync_type=stats["sync_type"],
                status="failed",
                error_message=str(error),
            )
            self.session.add(sync_status)
            self.session.commit()

        return stats

    def _full_sync(self) -> dict:
        """Full sync - parse all catalogs."""
        stats = {
            "factions_count": 0,
            "units_count": 0,
            "weapons_count": 0,
            "abilities_count": 0,
            "manifestations_count": 0,
            "battle_tactics_count": 0,
        }

        # Clear all existing data before full sync
        self._clear_all_data()
        self._ensure_grand_alliances()

        faction_catalogs = self.parser.get_faction_catalogs()
        for main_cat, lib_cat in faction_catalogs:
            faction_stats = self._sync_faction(main_cat, lib_cat)
            if faction_stats:
                stats["factions_count"] += 1
                stats["units_count"] += faction_stats.get("units", 0)
                stats["weapons_count"] += faction_stats.get("weapons", 0)
                stats["abilities_count"] += faction_stats.get("abilities", 0)

        gst_data = self.parser.parse_game_system()

        for manif_data in gst_data.get("manifestations", []):
            self._upsert_manifestation(manif_data)
            stats["manifestations_count"] += 1

        for card_data in gst_data.get("battle_tactic_cards", []):
            self._upsert_battle_tactic_card(card_data)
            stats["battle_tactics_count"] += 1

        for ability_data in gst_data.get("core_abilities", []):
            self._upsert_core_ability(ability_data)

        ror_data = self.parser.parse_regiments_of_renown()
        for regiment_data in ror_data:
            self._upsert_regiment_of_renown(regiment_data)
        stats["regiments_of_renown_count"] = len(ror_data)

        lores_data = self.parser.parse_lores()
        for lore_data in lores_data.get("spell_lores", []):
            self._upsert_spell_lore(lore_data)
        stats["spell_lores_count"] = len(lores_data.get("spell_lores", []))

        self.session.commit()
        return stats

    def _clear_all_data(self):
        """Clear all BSData tables before full sync."""
        from sqlalchemy import text

        # Delete in order respecting foreign keys
        self.session.exec(text("DELETE FROM bsdata_spells"))
        self.session.exec(text("DELETE FROM bsdata_spell_lores"))
        self.session.exec(text("DELETE FROM bsdata_ror_units"))
        self.session.exec(text("DELETE FROM bsdata_regiments_of_renown"))
        self.session.exec(text("DELETE FROM bsdata_weapons"))
        self.session.exec(text("DELETE FROM bsdata_unit_abilities"))
        self.session.exec(text("DELETE FROM bsdata_units"))
        self.session.exec(text("DELETE FROM bsdata_battle_traits"))
        self.session.exec(text("DELETE FROM bsdata_heroic_traits"))
        self.session.exec(text("DELETE FROM bsdata_artefacts"))
        self.session.exec(text("DELETE FROM bsdata_aor_battle_traits"))
        self.session.exec(text("DELETE FROM bsdata_armies_of_renown"))
        self.session.exec(text("DELETE FROM bsdata_factions"))
        self.session.exec(text("DELETE FROM bsdata_grand_alliances"))
        self.session.exec(text("DELETE FROM bsdata_manifestations"))
        self.session.exec(text("DELETE FROM bsdata_battle_tactic_cards"))
        self.session.exec(text("DELETE FROM bsdata_core_abilities"))
        self.session.commit()

        # Clear caches
        self._grand_alliance_cache.clear()
        self._faction_cache.clear()
        logger.info("Cleared all BSData tables")

    def _ensure_grand_alliances(self):
        """Ensure all grand alliances exist in database."""
        for alliance_name in ["Order", "Chaos", "Death", "Destruction"]:
            existing = self.session.exec(
                select(GrandAlliance).where(GrandAlliance.name == alliance_name)
            ).first()

            if not existing:
                alliance = GrandAlliance(name=alliance_name)
                self.session.add(alliance)
                self.session.flush()
                self._grand_alliance_cache[alliance_name] = alliance.id
            else:
                self._grand_alliance_cache[alliance_name] = existing.id

    def _get_or_create_faction(self, name: str, bsdata_id: str) -> int:
        """Get or create faction, return ID."""
        if bsdata_id in self._faction_cache:
            return self._faction_cache[bsdata_id]

        existing = self.session.exec(
            select(Faction).where(Faction.bsdata_id == bsdata_id)
        ).first()

        if existing:
            self._faction_cache[bsdata_id] = existing.id
            return existing.id

        alliance_name = get_grand_alliance(name)
        alliance_id = self._grand_alliance_cache.get(alliance_name)

        if not alliance_id:
            alliance_id = self._grand_alliance_cache.get("Order", 1)

        faction = Faction(
            name=name,
            bsdata_id=bsdata_id,
            grand_alliance_id=alliance_id,
        )
        self.session.add(faction)
        self.session.flush()

        self._faction_cache[bsdata_id] = faction.id
        return faction.id

    def _sync_faction(self, main_cat: Path, lib_cat: Optional[Path]) -> Optional[dict]:
        """Sync a single faction from its catalog files."""
        stats = {"units": 0, "weapons": 0, "abilities": 0}

        catalog_data = self.parser.parse_catalog(main_cat)
        faction_name = catalog_data.get("name", main_cat.stem)

        if any(
            skip in faction_name
            for skip in ["Regiments of Renown", "Lores", "Path to Glory", "[LEGENDS]"]
        ):
            return None
        if faction_name.startswith("þ"):
            return None

        is_army_of_renown = " - " in faction_name and "Library" not in faction_name

        if is_army_of_renown:
            self._sync_army_of_renown(main_cat, catalog_data)
            return None

        faction_id = self._get_or_create_faction(
            faction_name, catalog_data.get("bsdata_id", "")
        )

        points_data = self.parser.parse_faction_main_catalog(main_cat)
        points_map = points_data.get("points", {})

        if lib_cat and lib_cat.exists():
            lib_data = self.parser.parse_library_catalog(lib_cat)

            for unit_data in lib_data.get("units", []):
                unit_data["points"] = points_map.get(unit_data["name"])
                unit_stats = self._upsert_unit(faction_id, unit_data)
                stats["units"] += 1
                stats["weapons"] += unit_stats.get("weapons", 0)
                stats["abilities"] += unit_stats.get("abilities", 0)

            for trait_data in lib_data.get("battle_traits", []):
                self._upsert_battle_trait(faction_id, trait_data)

            for trait_data in lib_data.get("heroic_traits", []):
                self._upsert_heroic_trait(faction_id, trait_data)

            for artefact_data in lib_data.get("artefacts", []):
                self._upsert_artefact(faction_id, artefact_data)

        return stats

    def _sync_army_of_renown(self, cat_path: Path, catalog_data: dict):
        """Sync an Army of Renown."""
        full_name = catalog_data.get("name", "")
        bsdata_id = catalog_data.get("bsdata_id", "")

        parts = full_name.split(" - ", 1)
        if len(parts) != 2:
            return

        parent_faction_name = parts[0]
        aor_name = parts[1]

        parent_faction = self.session.exec(
            select(Faction).where(Faction.name == parent_faction_name)
        ).first()

        if not parent_faction:
            return

        existing = self.session.exec(
            select(ArmyOfRenown).where(ArmyOfRenown.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = aor_name
        else:
            aor = ArmyOfRenown(
                name=aor_name,
                bsdata_id=bsdata_id,
                faction_id=parent_faction.id,
            )
            self.session.add(aor)

    def _upsert_unit(self, faction_id: int, unit_data: dict) -> dict:
        """Upsert a unit and its weapons/abilities."""
        stats = {"weapons": 0, "abilities": 0}

        bsdata_id = unit_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(Unit).where(Unit.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = unit_data.get("name", existing.name)
            existing.points = unit_data.get("points", existing.points)
            existing.move = unit_data.get("move", existing.move)
            existing.health = unit_data.get("health", existing.health)
            existing.save = unit_data.get("save", existing.save)
            existing.control = unit_data.get("control", existing.control)
            unit = existing
        else:
            unit = Unit(
                faction_id=faction_id,
                bsdata_id=bsdata_id,
                name=unit_data.get("name", ""),
                points=unit_data.get("points"),
                move=unit_data.get("move"),
                health=unit_data.get("health"),
                save=unit_data.get("save"),
                control=unit_data.get("control"),
            )
            self.session.add(unit)
            self.session.flush()

        for weapon_data in unit_data.get("weapons", []):
            self._upsert_weapon(unit.id, weapon_data)
            stats["weapons"] += 1

        for ability_data in unit_data.get("abilities", []):
            self._upsert_unit_ability(unit.id, ability_data)
            stats["abilities"] += 1

        return stats

    def _upsert_weapon(self, unit_id: int, weapon_data: dict):
        """Upsert a weapon."""
        bsdata_id = weapon_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(Weapon).where(Weapon.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = weapon_data.get("name", existing.name)
            existing.weapon_type = weapon_data.get("weapon_type", existing.weapon_type)
            existing.range = weapon_data.get("range", existing.range)
            existing.attacks = weapon_data.get("attacks", existing.attacks)
            existing.hit = weapon_data.get("hit", existing.hit)
            existing.wound = weapon_data.get("wound", existing.wound)
            existing.rend = weapon_data.get("rend", existing.rend)
            existing.damage = weapon_data.get("damage", existing.damage)
            existing.ability = weapon_data.get("ability", existing.ability)
        else:
            weapon = Weapon(
                unit_id=unit_id,
                bsdata_id=bsdata_id,
                name=weapon_data.get("name", ""),
                weapon_type=weapon_data.get("weapon_type", "melee"),
                range=weapon_data.get("range"),
                attacks=weapon_data.get("attacks"),
                hit=weapon_data.get("hit"),
                wound=weapon_data.get("wound"),
                rend=weapon_data.get("rend"),
                damage=weapon_data.get("damage"),
                ability=weapon_data.get("ability"),
            )
            self.session.add(weapon)

    def _upsert_unit_ability(self, unit_id: int, ability_data: dict):
        """Upsert a unit ability."""
        bsdata_id = ability_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(UnitAbility).where(UnitAbility.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = ability_data.get("name", existing.name)
            existing.ability_type = ability_data.get(
                "ability_type", existing.ability_type
            )
            existing.effect = ability_data.get("effect", existing.effect)
            existing.keywords = ability_data.get("keywords", existing.keywords)
        else:
            ability = UnitAbility(
                unit_id=unit_id,
                bsdata_id=bsdata_id,
                name=ability_data.get("name", ""),
                ability_type=ability_data.get("ability_type", "passive"),
                effect=ability_data.get("effect"),
                keywords=ability_data.get("keywords"),
            )
            self.session.add(ability)

    def _upsert_battle_trait(self, faction_id: int, trait_data: dict):
        """Upsert a battle trait."""
        bsdata_id = trait_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(BattleTrait).where(BattleTrait.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = trait_data.get("name", existing.name)
            existing.effect = trait_data.get("effect", existing.effect)
        else:
            trait = BattleTrait(
                faction_id=faction_id,
                bsdata_id=bsdata_id,
                name=trait_data.get("name", ""),
                effect=trait_data.get("effect"),
            )
            self.session.add(trait)

    def _upsert_heroic_trait(self, faction_id: int, trait_data: dict):
        """Upsert a heroic trait."""
        bsdata_id = trait_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(HeroicTrait).where(HeroicTrait.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = trait_data.get("name", existing.name)
            existing.effect = trait_data.get("effect", existing.effect)
        else:
            trait = HeroicTrait(
                faction_id=faction_id,
                bsdata_id=bsdata_id,
                name=trait_data.get("name", ""),
                effect=trait_data.get("effect"),
            )
            self.session.add(trait)

    def _upsert_artefact(self, faction_id: int, artefact_data: dict):
        """Upsert an artefact."""
        bsdata_id = artefact_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(Artefact).where(Artefact.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = artefact_data.get("name", existing.name)
            existing.effect = artefact_data.get("effect", existing.effect)
        else:
            artefact = Artefact(
                faction_id=faction_id,
                bsdata_id=bsdata_id,
                name=artefact_data.get("name", ""),
                effect=artefact_data.get("effect"),
            )
            self.session.add(artefact)

    def _upsert_manifestation(self, manif_data: dict):
        """Upsert a manifestation."""
        bsdata_id = manif_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(Manifestation).where(Manifestation.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = manif_data.get("name", existing.name)
            existing.move = manif_data.get("move", existing.move)
            existing.health = manif_data.get("health", existing.health)
            existing.save = manif_data.get("save", existing.save)
            existing.banishment = manif_data.get("banishment", existing.banishment)
        else:
            manif = Manifestation(
                bsdata_id=bsdata_id,
                name=manif_data.get("name", ""),
                move=manif_data.get("move"),
                health=manif_data.get("health"),
                save=manif_data.get("save"),
                banishment=manif_data.get("banishment"),
            )
            self.session.add(manif)

    def _upsert_battle_tactic_card(self, card_data: dict):
        """Upsert a battle tactic card."""
        bsdata_id = card_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(BattleTacticCard).where(BattleTacticCard.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = card_data.get("name", existing.name)
            existing.card_rules = card_data.get("card_rules", existing.card_rules)
            existing.affray_name = card_data.get("affray_name", existing.affray_name)
            existing.affray_effect = card_data.get(
                "affray_effect", existing.affray_effect
            )
            existing.strike_name = card_data.get("strike_name", existing.strike_name)
            existing.strike_effect = card_data.get(
                "strike_effect", existing.strike_effect
            )
            existing.domination_name = card_data.get(
                "domination_name", existing.domination_name
            )
            existing.domination_effect = card_data.get(
                "domination_effect", existing.domination_effect
            )
        else:
            card = BattleTacticCard(
                bsdata_id=bsdata_id,
                name=card_data.get("name", ""),
                card_rules=card_data.get("card_rules"),
                affray_name=card_data.get("affray_name"),
                affray_effect=card_data.get("affray_effect"),
                strike_name=card_data.get("strike_name"),
                strike_effect=card_data.get("strike_effect"),
                domination_name=card_data.get("domination_name"),
                domination_effect=card_data.get("domination_effect"),
            )
            self.session.add(card)

    def _upsert_core_ability(self, ability_data: dict):
        """Upsert a core ability."""
        bsdata_id = ability_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(CoreAbility).where(CoreAbility.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = ability_data.get("name", existing.name)
            existing.ability_type = ability_data.get(
                "ability_type", existing.ability_type
            )
            existing.effect = ability_data.get("effect", existing.effect)
            existing.keywords = ability_data.get("keywords", existing.keywords)
        else:
            ability = CoreAbility(
                bsdata_id=bsdata_id,
                name=ability_data.get("name", ""),
                ability_type=ability_data.get("ability_type", "passive"),
                effect=ability_data.get("effect"),
                keywords=ability_data.get("keywords"),
            )
            self.session.add(ability)

    def _upsert_regiment_of_renown(self, regiment_data: dict):
        """Upsert a Regiment of Renown."""
        bsdata_id = regiment_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(RegimentOfRenown).where(RegimentOfRenown.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = regiment_data.get("name", existing.name)
            existing.points = regiment_data.get("points", existing.points)
            existing.description = regiment_data.get(
                "description", existing.description
            )
        else:
            regiment = RegimentOfRenown(
                bsdata_id=bsdata_id,
                name=regiment_data.get("name", ""),
                points=regiment_data.get("points"),
                description=regiment_data.get("description"),
            )
            self.session.add(regiment)

    def _upsert_spell_lore(self, lore_data: dict):
        """Upsert a spell lore with its spells."""
        bsdata_id = lore_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(SpellLore).where(SpellLore.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = lore_data.get("name", existing.name)
            lore = existing
        else:
            lore = SpellLore(
                bsdata_id=bsdata_id,
                name=lore_data.get("name", ""),
            )
            self.session.add(lore)
            self.session.flush()

        for spell_data in lore_data.get("spells", []):
            self._upsert_spell(lore.id, spell_data)

    def _upsert_spell(self, lore_id: int, spell_data: dict):
        """Upsert a spell."""
        bsdata_id = spell_data.get("bsdata_id", "")
        existing = self.session.exec(
            select(Spell).where(Spell.bsdata_id == bsdata_id)
        ).first()

        if existing:
            existing.name = spell_data.get("name", existing.name)
            existing.casting_value = spell_data.get(
                "casting_value", existing.casting_value
            )
            existing.effect = spell_data.get("effect", existing.effect)
        else:
            spell = Spell(
                lore_id=lore_id,
                bsdata_id=bsdata_id,
                name=spell_data.get("name", ""),
                casting_value=spell_data.get("casting_value"),
                effect=spell_data.get("effect"),
            )
            self.session.add(spell)

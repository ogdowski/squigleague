"""BSData synchronization service using GitHub API (no git required)."""

import io
import json
import logging
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from app.bsdata.models import (
    Artefact,
    BattleFormation,
    BattleTacticCard,
    BattleTrait,
    BSDataSyncStatus,
    CoreAbility,
    Faction,
    GrandAlliance,
    HeroicTrait,
    Manifestation,
    ManifestationLore,
    Prayer,
    PrayerLore,
    RegimentOfRenown,
    RoRUnit,
    Spell,
    SpellLore,
    Unit,
    UnitAbility,
    UnitFaction,
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

    # Unicode quote characters to normalize to ASCII apostrophe
    _QUOTE_MAP = str.maketrans(
        {
            "\u2018": "'",  # LEFT SINGLE QUOTATION MARK
            "\u2019": "'",  # RIGHT SINGLE QUOTATION MARK
            "\u201C": '"',  # LEFT DOUBLE QUOTATION MARK
            "\u201D": '"',  # RIGHT DOUBLE QUOTATION MARK
        }
    )

    def __init__(self, session: Session):
        self.session = session
        self.repo_path = BSDATA_LOCAL_PATH
        self.parser: Optional[BSDataParser] = None
        self._grand_alliance_cache: dict[str, int] = {}
        self._faction_cache: dict[str, int] = {}
        self._lores_index: dict = {}
        self._manifestation_stats_cache: dict[str, dict] = {}

    @classmethod
    def _normalize_cache_key(cls, name: str) -> str:
        """Normalize a manifestation name for cache key lookup.

        Handles Unicode quote differences between BSData files.
        """
        return name.lower().translate(cls._QUOTE_MAP)

    def get_current_commit(self) -> Optional[str]:
        """Get current BSData commit from database."""
        statement = (
            select(BSDataSyncStatus)
            .where(BSDataSyncStatus.status == "success")
            .order_by(BSDataSyncStatus.synced_at.desc())
        )
        status = self.session.execute(statement).scalars().first()
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

        # ── Phase 1: Build manifestation stats cache BEFORE faction sync ──
        # GST manifestation profiles (universal manifestations)
        gst_data = self.parser.parse_game_system()
        for manif_data in gst_data.get("manifestations", []):
            self._upsert_manifestation(manif_data)
            manif_name = manif_data.get("name", "")
            if manif_name:
                self._manifestation_stats_cache[
                    self._normalize_cache_key(manif_name)
                ] = {
                    "move": manif_data.get("move"),
                    "health": manif_data.get("health"),
                    "save": manif_data.get("save"),
                    "banishment": manif_data.get("banishment"),
                    "weapons": manif_data.get("weapons", []),
                    "abilities": manif_data.get("abilities", []),
                }
            stats["manifestations_count"] += 1

        # Library.cat manifestation profiles (faction-specific manifestations)
        faction_catalogs = self.parser.get_faction_catalogs()
        for main_cat, lib_cat in faction_catalogs:
            if lib_cat and lib_cat.exists():
                lib_data = self.parser.parse_library_catalog(lib_cat)
                for manif_data in lib_data.get("manifestations", []):
                    manif_name = manif_data.get("name", "")
                    if manif_name:
                        self._manifestation_stats_cache[
                            self._normalize_cache_key(manif_name)
                        ] = {
                            "move": manif_data.get("move"),
                            "health": manif_data.get("health"),
                            "save": manif_data.get("save"),
                            "banishment": manif_data.get("banishment"),
                            "weapons": manif_data.get("weapons", []),
                            "abilities": manif_data.get("abilities", []),
                        }

        # ── Phase 2: Build lores index and sync factions ──
        self._lores_index = self.parser.parse_lores_indexed()

        for main_cat, lib_cat in faction_catalogs:
            faction_stats = self._sync_faction(main_cat, lib_cat)
            if faction_stats:
                stats["factions_count"] += 1
                stats["units_count"] += faction_stats.get("units", 0)
                stats["weapons_count"] += faction_stats.get("weapons", 0)
                stats["abilities_count"] += faction_stats.get("abilities", 0)

        # ── Phase 3: Core content (battle tactics, core abilities, etc.) ──
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

        # ── Phase 4: Universal manifestation lores ──
        universal_lores = self.parser.parse_universal_manifestation_lores()
        for lore_data in universal_lores:
            self._upsert_universal_manifestation_lore(lore_data)

        self.session.commit()
        return stats

    def _clear_all_data(self):
        """Clear all BSData tables before full sync."""
        from sqlalchemy import text

        # Delete in order respecting foreign keys
        tables_to_clear = [
            "bsdata_spells",
            "bsdata_spell_lores",
            "bsdata_prayers",
            "bsdata_prayer_lores",
            "bsdata_manifestations",
            "bsdata_manifestation_lores",
            "bsdata_ror_units",
            "bsdata_regiments_of_renown",
            "bsdata_unit_factions",
            "bsdata_weapons",
            "bsdata_unit_abilities",
            "bsdata_units",
            "bsdata_battle_traits",
            "bsdata_battle_formations",
            "bsdata_heroic_traits",
            "bsdata_artefacts",
            "bsdata_factions",
            "bsdata_grand_alliances",
            "bsdata_battle_tactic_cards",
            "bsdata_core_abilities",
        ]
        for table_name in tables_to_clear:
            self.session.execute(text(f"DELETE FROM {table_name}"))
        self.session.commit()

        # Clear caches
        self._grand_alliance_cache.clear()
        self._faction_cache.clear()
        self._manifestation_stats_cache.clear()
        logger.info("Cleared all BSData tables")

    def _ensure_grand_alliances(self):
        """Ensure all grand alliances exist in database."""
        for alliance_name in ["Order", "Chaos", "Death", "Destruction"]:
            statement = select(GrandAlliance).where(GrandAlliance.name == alliance_name)
            existing = self.session.execute(statement).scalars().first()

            if not existing:
                alliance = GrandAlliance(name=alliance_name)
                self.session.add(alliance)
                self.session.flush()
                self._grand_alliance_cache[alliance_name] = alliance.id
            else:
                self._grand_alliance_cache[alliance_name] = existing.id

    def _get_or_create_faction(
        self,
        name: str,
        bsdata_id: str,
        is_aor: bool = False,
        parent_faction_id: Optional[int] = None,
    ) -> int:
        """Get or create faction, return ID."""
        if bsdata_id in self._faction_cache:
            return self._faction_cache[bsdata_id]

        statement = select(Faction).where(Faction.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            self._faction_cache[bsdata_id] = existing.id
            return existing.id

        # For AoR factions, use the parent faction's grand alliance
        if is_aor and parent_faction_id:
            parent = self.session.get(Faction, parent_faction_id)
            alliance_id = (
                parent.grand_alliance_id
                if parent
                else self._grand_alliance_cache.get("Order", 1)
            )
        else:
            alliance_name = get_grand_alliance(name)
            alliance_id = self._grand_alliance_cache.get(alliance_name)
            if not alliance_id:
                alliance_id = self._grand_alliance_cache.get("Order", 1)

        faction = Faction(
            name=name,
            bsdata_id=bsdata_id,
            grand_alliance_id=alliance_id,
            is_aor=is_aor,
            parent_faction_id=parent_faction_id,
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
            for skip in [
                "Regiments of Renown",
                "Lores",
                "Path to Glory",
                "[LEGENDS]",
                "Anvil of Apotheosis",
            ]
        ):
            return None
        if faction_name.startswith("\u00fe"):
            return None

        is_army_of_renown = " - " in faction_name and "Library" not in faction_name

        if is_army_of_renown:
            self._sync_army_of_renown(main_cat, catalog_data)
            return {"units": 0, "weapons": 0, "abilities": 0}

        faction_id = self._get_or_create_faction(
            faction_name, catalog_data.get("bsdata_id", "")
        )

        self._sync_faction_content(faction_id, main_cat, lib_cat, stats)
        return stats

    def _sync_faction_content(
        self,
        faction_id: int,
        main_cat: Path,
        lib_cat: Optional[Path],
        stats: dict,
    ):
        """Sync all content for a faction (battle traits, lores, units, etc.)."""
        main_data = self.parser.parse_faction_main_catalog(main_cat)
        points_map = main_data.get("points", {})
        reinforced_units = main_data.get("reinforced_units", set())
        notes_map = main_data.get("notes", {})

        # Battle traits, heroic traits, artefacts from main catalog
        for trait_data in main_data.get("battle_traits", []):
            self._upsert_battle_trait(faction_id, trait_data)

        for trait_data in main_data.get("heroic_traits", []):
            self._upsert_heroic_trait(faction_id, trait_data)

        for artefact_data in main_data.get("artefacts", []):
            self._upsert_artefact(faction_id, artefact_data)

        for formation_data in main_data.get("battle_formations", []):
            self._upsert_battle_formation(faction_id, formation_data)

        # Resolve spell lore references via Lores.cat index
        for lore_ref in main_data.get("spell_lore_refs", []):
            lore_content = self._lores_index.get(lore_ref["target_id"])
            if lore_content:
                self._upsert_faction_spell_lore(
                    faction_id,
                    lore_ref["target_id"],
                    lore_ref["name"],
                    lore_content["entries"],
                    lore_ref.get("points"),
                )

        # Resolve prayer lore references (now stored in prayer tables)
        for lore_ref in main_data.get("prayer_lore_refs", []):
            lore_content = self._lores_index.get(lore_ref["target_id"])
            if lore_content:
                self._upsert_faction_prayer_lore(
                    faction_id,
                    lore_ref["target_id"],
                    lore_ref["name"],
                    lore_content["entries"],
                    lore_ref.get("points"),
                )

        # Resolve manifestation lore references
        for lore_ref in main_data.get("manifestation_lore_refs", []):
            lore_content = self._lores_index.get(lore_ref["target_id"])
            if lore_content:
                self._upsert_faction_manifestation_lore(
                    faction_id,
                    lore_ref["target_id"],
                    lore_ref["name"],
                    lore_content["entries"],
                )

        # Units from library catalog
        if lib_cat and lib_cat.exists():
            lib_data = self.parser.parse_library_catalog(lib_cat)

            for unit_data in lib_data.get("units", []):
                unit_name = unit_data["name"]
                unit_data["points"] = points_map.get(unit_name)
                unit_data["can_be_reinforced"] = unit_name in reinforced_units
                unit_data["notes"] = notes_map.get(unit_name)
                unit_stats = self._upsert_unit(faction_id, unit_data)
                stats["units"] += 1
                stats["weapons"] += unit_stats.get("weapons", 0)
                stats["abilities"] += unit_stats.get("abilities", 0)

        # AoR unit references — link parent faction's units by name
        unit_ref_names = {ref["name"] for ref in main_data.get("unit_refs", [])}
        if unit_ref_names:
            self._link_aor_units(faction_id, unit_ref_names, stats)

    def _sync_army_of_renown(self, cat_path: Path, catalog_data: dict):
        """Sync an Army of Renown as a regular faction with is_aor=True."""
        full_name = catalog_data.get("name", "")
        bsdata_id = catalog_data.get("bsdata_id", "")

        parts = full_name.split(" - ", 1)
        if len(parts) != 2:
            return

        parent_faction_name = parts[0]
        aor_name = parts[1]

        statement = select(Faction).where(Faction.name == parent_faction_name)
        parent_faction = self.session.execute(statement).scalars().first()

        if not parent_faction:
            return

        # Create AoR as a regular faction with is_aor flag
        faction_id = self._get_or_create_faction(
            aor_name,
            bsdata_id,
            is_aor=True,
            parent_faction_id=parent_faction.id,
        )

        # Parse AoR catalog the same way as a normal faction
        # AoRs have battle traits, heroic traits, artefacts, spell lores etc.
        # They typically don't have battle formations or their own units
        stats = {"units": 0, "weapons": 0, "abilities": 0}
        self._sync_faction_content(faction_id, cat_path, None, stats)

    def _link_aor_units(self, aor_faction_id: int, unit_ref_names: set, stats: dict):
        """Link parent faction units to AoR via junction table."""
        aor_faction = self.session.get(Faction, aor_faction_id)
        if not aor_faction or not aor_faction.parent_faction_id:
            return

        statement = select(Unit).where(Unit.faction_id == aor_faction.parent_faction_id)
        parent_units = self.session.execute(statement).scalars().all()

        for parent_unit in parent_units:
            if parent_unit.name in unit_ref_names:
                link = UnitFaction(
                    unit_id=parent_unit.id,
                    faction_id=aor_faction_id,
                )
                self.session.add(link)
                stats["units"] += 1

    def _upsert_unit(self, faction_id: int, unit_data: dict) -> dict:
        """Upsert a unit and its weapons/abilities."""
        stats = {"weapons": 0, "abilities": 0}

        bsdata_id = unit_data.get("bsdata_id", "")
        keywords_list = unit_data.get("keywords", [])
        keywords_json = json.dumps(keywords_list) if keywords_list else None

        statement = select(Unit).where(Unit.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = unit_data.get("name", existing.name)
            existing.points = unit_data.get("points", existing.points)
            existing.move = unit_data.get("move", existing.move)
            existing.health = unit_data.get("health", existing.health)
            existing.save = unit_data.get("save", existing.save)
            existing.control = unit_data.get("control", existing.control)
            existing.keywords = keywords_json
            existing.base_size = unit_data.get("base_size", existing.base_size)
            existing.unit_size = unit_data.get("unit_size", existing.unit_size)
            existing.can_be_reinforced = unit_data.get(
                "can_be_reinforced", existing.can_be_reinforced
            )
            existing.notes = unit_data.get("notes", existing.notes)
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
                keywords=keywords_json,
                base_size=unit_data.get("base_size"),
                unit_size=unit_data.get("unit_size"),
                can_be_reinforced=unit_data.get("can_be_reinforced", False),
                notes=unit_data.get("notes"),
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
        statement = select(Weapon).where(Weapon.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

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
        statement = select(UnitAbility).where(UnitAbility.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = ability_data.get("name", existing.name)
            existing.ability_type = ability_data.get(
                "ability_type", existing.ability_type
            )
            existing.effect = ability_data.get("effect", existing.effect)
            existing.keywords = ability_data.get("keywords", existing.keywords)
            existing.timing = ability_data.get("timing", existing.timing)
            existing.declare = ability_data.get("declare", existing.declare)
            existing.color = ability_data.get("color", existing.color)
        else:
            ability = UnitAbility(
                unit_id=unit_id,
                bsdata_id=bsdata_id,
                name=ability_data.get("name", ""),
                ability_type=ability_data.get("ability_type", "passive"),
                effect=ability_data.get("effect"),
                keywords=ability_data.get("keywords"),
                timing=ability_data.get("timing"),
                declare=ability_data.get("declare"),
                color=ability_data.get("color"),
            )
            self.session.add(ability)

    def _upsert_battle_trait(self, faction_id: int, trait_data: dict):
        """Upsert a battle trait."""
        bsdata_id = trait_data.get("bsdata_id", "")
        statement = select(BattleTrait).where(BattleTrait.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = trait_data.get("name", existing.name)
            existing.effect = trait_data.get("effect", existing.effect)
            existing.timing = trait_data.get("timing", existing.timing)
            existing.declare = trait_data.get("declare", existing.declare)
            existing.color = trait_data.get("color", existing.color)
            existing.keywords = trait_data.get("keywords", existing.keywords)
        else:
            trait = BattleTrait(
                faction_id=faction_id,
                bsdata_id=bsdata_id,
                name=trait_data.get("name", ""),
                effect=trait_data.get("effect"),
                timing=trait_data.get("timing"),
                declare=trait_data.get("declare"),
                color=trait_data.get("color"),
                keywords=trait_data.get("keywords"),
            )
            self.session.add(trait)

    def _upsert_heroic_trait(self, faction_id: int, trait_data: dict):
        """Upsert a heroic trait."""
        bsdata_id = trait_data.get("bsdata_id", "")
        statement = select(HeroicTrait).where(HeroicTrait.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = trait_data.get("name", existing.name)
            existing.points = trait_data.get("points")
            existing.effect = trait_data.get("effect", existing.effect)
            existing.timing = trait_data.get("timing", existing.timing)
            existing.declare = trait_data.get("declare", existing.declare)
            existing.color = trait_data.get("color", existing.color)
            existing.keywords = trait_data.get("keywords", existing.keywords)
            existing.group_name = trait_data.get("group_name", existing.group_name)
            existing.is_seasonal = trait_data.get("is_seasonal", existing.is_seasonal)
        else:
            trait = HeroicTrait(
                faction_id=faction_id,
                bsdata_id=bsdata_id,
                name=trait_data.get("name", ""),
                points=trait_data.get("points"),
                effect=trait_data.get("effect"),
                timing=trait_data.get("timing"),
                declare=trait_data.get("declare"),
                color=trait_data.get("color"),
                keywords=trait_data.get("keywords"),
                group_name=trait_data.get("group_name"),
                is_seasonal=trait_data.get("is_seasonal", False),
            )
            self.session.add(trait)

    def _upsert_artefact(self, faction_id: int, artefact_data: dict):
        """Upsert an artefact."""
        bsdata_id = artefact_data.get("bsdata_id", "")
        statement = select(Artefact).where(Artefact.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = artefact_data.get("name", existing.name)
            existing.points = artefact_data.get("points")
            existing.effect = artefact_data.get("effect", existing.effect)
            existing.timing = artefact_data.get("timing", existing.timing)
            existing.declare = artefact_data.get("declare", existing.declare)
            existing.color = artefact_data.get("color", existing.color)
            existing.keywords = artefact_data.get("keywords", existing.keywords)
            existing.group_name = artefact_data.get("group_name", existing.group_name)
            existing.is_seasonal = artefact_data.get(
                "is_seasonal", existing.is_seasonal
            )
        else:
            artefact = Artefact(
                faction_id=faction_id,
                bsdata_id=bsdata_id,
                name=artefact_data.get("name", ""),
                points=artefact_data.get("points"),
                effect=artefact_data.get("effect"),
                timing=artefact_data.get("timing"),
                declare=artefact_data.get("declare"),
                color=artefact_data.get("color"),
                keywords=artefact_data.get("keywords"),
                group_name=artefact_data.get("group_name"),
                is_seasonal=artefact_data.get("is_seasonal", False),
            )
            self.session.add(artefact)

    def _upsert_battle_formation(self, faction_id: int, formation_data: dict):
        """Upsert a battle formation."""
        bsdata_id = formation_data.get("bsdata_id", "")
        statement = select(BattleFormation).where(
            BattleFormation.bsdata_id == bsdata_id
        )
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = formation_data.get("name", existing.name)
            existing.points = formation_data.get("points")
            existing.ability_name = formation_data.get("ability_name")
            existing.ability_type = formation_data.get("ability_type")
            existing.effect = formation_data.get("effect")
            existing.timing = formation_data.get("timing")
            existing.declare = formation_data.get("declare")
            existing.color = formation_data.get("color")
            existing.keywords = formation_data.get("keywords")
        else:
            formation = BattleFormation(
                faction_id=faction_id,
                bsdata_id=bsdata_id,
                name=formation_data.get("name", ""),
                points=formation_data.get("points"),
                ability_name=formation_data.get("ability_name"),
                ability_type=formation_data.get("ability_type"),
                effect=formation_data.get("effect"),
                timing=formation_data.get("timing"),
                declare=formation_data.get("declare"),
                color=formation_data.get("color"),
                keywords=formation_data.get("keywords"),
            )
            self.session.add(formation)

    def _upsert_manifestation(self, manif_data: dict):
        """Upsert a manifestation."""
        bsdata_id = manif_data.get("bsdata_id", "")
        weapons_json = (
            json.dumps(manif_data["weapons"]) if manif_data.get("weapons") else None
        )
        abilities_json = (
            json.dumps(manif_data["abilities"]) if manif_data.get("abilities") else None
        )

        statement = select(Manifestation).where(Manifestation.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = manif_data.get("name", existing.name)
            existing.move = manif_data.get("move", existing.move)
            existing.health = manif_data.get("health", existing.health)
            existing.save = manif_data.get("save", existing.save)
            existing.banishment = manif_data.get("banishment", existing.banishment)
            if weapons_json:
                existing.weapons = weapons_json
            if abilities_json:
                existing.abilities = abilities_json
        else:
            manif = Manifestation(
                bsdata_id=bsdata_id,
                name=manif_data.get("name", ""),
                move=manif_data.get("move"),
                health=manif_data.get("health"),
                save=manif_data.get("save"),
                banishment=manif_data.get("banishment"),
                weapons=weapons_json,
                abilities=abilities_json,
            )
            self.session.add(manif)

    def _upsert_battle_tactic_card(self, card_data: dict):
        """Upsert a battle tactic card."""
        bsdata_id = card_data.get("bsdata_id", "")
        statement = select(BattleTacticCard).where(
            BattleTacticCard.bsdata_id == bsdata_id
        )
        existing = self.session.execute(statement).scalars().first()

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
        """Upsert a core ability (with full ability fields)."""
        bsdata_id = ability_data.get("bsdata_id", "")
        statement = select(CoreAbility).where(CoreAbility.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = ability_data.get("name", existing.name)
            existing.ability_type = ability_data.get(
                "ability_type", existing.ability_type
            )
            existing.effect = ability_data.get("effect", existing.effect)
            existing.keywords = ability_data.get("keywords", existing.keywords)
            existing.timing = ability_data.get("timing", existing.timing)
            existing.declare = ability_data.get("declare", existing.declare)
            existing.color = ability_data.get("color", existing.color)
        else:
            ability = CoreAbility(
                bsdata_id=bsdata_id,
                name=ability_data.get("name", ""),
                ability_type=ability_data.get("ability_type", "passive"),
                effect=ability_data.get("effect"),
                keywords=ability_data.get("keywords"),
                timing=ability_data.get("timing"),
                declare=ability_data.get("declare"),
                color=ability_data.get("color"),
            )
            self.session.add(ability)

    def _upsert_regiment_of_renown(self, regiment_data: dict):
        """Upsert a Regiment of Renown."""
        bsdata_id = regiment_data.get("bsdata_id", "")
        statement = select(RegimentOfRenown).where(
            RegimentOfRenown.bsdata_id == bsdata_id
        )
        existing = self.session.execute(statement).scalars().first()

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
        statement = select(SpellLore).where(SpellLore.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

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
        statement = select(Spell).where(Spell.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = spell_data.get("name", existing.name)
            existing.casting_value = spell_data.get(
                "casting_value", existing.casting_value
            )
            existing.declare = spell_data.get("declare", existing.declare)
            existing.effect = spell_data.get("effect", existing.effect)
            existing.keywords = spell_data.get("keywords", existing.keywords)
        else:
            spell = Spell(
                lore_id=lore_id,
                bsdata_id=bsdata_id,
                name=spell_data.get("name", ""),
                casting_value=spell_data.get("casting_value"),
                declare=spell_data.get("declare"),
                effect=spell_data.get("effect"),
                keywords=spell_data.get("keywords"),
            )
            self.session.add(spell)

    def _upsert_faction_spell_lore(
        self,
        faction_id: int,
        bsdata_id: str,
        lore_name: str,
        entries: list,
        points: Optional[int] = None,
    ):
        """Upsert a faction-specific spell lore resolved from Lores.cat."""
        statement = select(SpellLore).where(SpellLore.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = lore_name
            existing.faction_id = faction_id
            existing.points = points
            lore = existing
        else:
            lore = SpellLore(
                bsdata_id=bsdata_id,
                faction_id=faction_id,
                name=lore_name,
                points=points,
            )
            self.session.add(lore)
            self.session.flush()

        for entry_data in entries:
            self._upsert_spell(lore.id, entry_data)

    def _upsert_faction_prayer_lore(
        self,
        faction_id: int,
        bsdata_id: str,
        lore_name: str,
        entries: list,
        points: Optional[int] = None,
    ):
        """Upsert a faction-specific prayer lore resolved from Lores.cat."""
        statement = select(PrayerLore).where(PrayerLore.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = lore_name
            existing.faction_id = faction_id
            existing.points = points
            lore = existing
        else:
            lore = PrayerLore(
                bsdata_id=bsdata_id,
                faction_id=faction_id,
                name=lore_name,
                points=points,
            )
            self.session.add(lore)
            self.session.flush()

        for entry_data in entries:
            self._upsert_prayer(lore.id, entry_data)

    def _upsert_prayer(self, lore_id: int, prayer_data: dict):
        """Upsert a prayer."""
        bsdata_id = prayer_data.get("bsdata_id", "")
        statement = select(Prayer).where(Prayer.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = prayer_data.get("name", existing.name)
            existing.chanting_value = prayer_data.get(
                "casting_value", existing.chanting_value
            )
            existing.declare = prayer_data.get("declare", existing.declare)
            existing.effect = prayer_data.get("effect", existing.effect)
            existing.keywords = prayer_data.get("keywords", existing.keywords)
        else:
            prayer = Prayer(
                lore_id=lore_id,
                bsdata_id=bsdata_id,
                name=prayer_data.get("name", ""),
                chanting_value=prayer_data.get("casting_value"),
                declare=prayer_data.get("declare"),
                effect=prayer_data.get("effect"),
                keywords=prayer_data.get("keywords"),
            )
            self.session.add(prayer)

    def _upsert_faction_manifestation_lore(
        self, faction_id: int, bsdata_id: str, lore_name: str, entries: list
    ):
        """Upsert a faction-specific manifestation lore resolved from Lores.cat."""
        statement = select(ManifestationLore).where(
            ManifestationLore.bsdata_id == bsdata_id
        )
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = lore_name
            existing.faction_id = faction_id
            lore = existing
        else:
            lore = ManifestationLore(
                bsdata_id=bsdata_id,
                faction_id=faction_id,
                name=lore_name,
            )
            self.session.add(lore)
            self.session.flush()

        for entry_data in entries:
            self._upsert_faction_manifestation(lore.id, entry_data)

    def _upsert_universal_manifestation_lore(self, lore_data: dict):
        """Upsert a universal manifestation lore (Morbid Conjuration, etc.).

        These have faction_id=NULL and are available to all armies.
        The lore_data contains a target_id pointing to the actual lore group
        in the lores index, whose entries contain the summoning spells.
        """
        bsdata_id = lore_data["bsdata_id"]
        lore_name = lore_data["name"]
        points = lore_data.get("points")
        target_id = lore_data.get("target_id")

        statement = select(ManifestationLore).where(
            ManifestationLore.bsdata_id == bsdata_id
        )
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = lore_name
            existing.faction_id = None
            existing.points = points
            lore = existing
        else:
            lore = ManifestationLore(
                bsdata_id=bsdata_id,
                faction_id=None,
                name=lore_name,
                points=points,
            )
            self.session.add(lore)
            self.session.flush()

        # Resolve target lore group from lores index
        if target_id and self._lores_index:
            lore_content = self._lores_index.get(target_id)
            if lore_content:
                for entry_data in lore_content.get("entries", []):
                    self._upsert_faction_manifestation(lore.id, entry_data)

    def _upsert_faction_manifestation(self, lore_id: int, entry_data: dict):
        """Upsert a manifestation entry (summoning spell stored as manifestation).

        Merges stats (move/health/save/banishment) and weapons/abilities from two sources:
        1. entry_data itself (parsed directly from Lores.cat selectionEntry profiles)
        2. GST manifestation stats cache (fallback for universal manifestations)
        Entry-level data takes priority over cache.
        """
        bsdata_id = entry_data.get("bsdata_id", "")
        manif_name = entry_data.get("name", "")

        # Look up stats from manifestation stats cache by name.
        # Lore entries use "Summon X" while cache uses the model name directly.
        # Also handles "The X" prefix mismatch and Unicode quote normalization.
        lookup_name = self._normalize_cache_key(manif_name)
        cached_stats = self._manifestation_stats_cache.get(lookup_name, {})
        if not cached_stats and lookup_name.startswith("summon "):
            stripped = lookup_name.removeprefix("summon ")
            cached_stats = self._manifestation_stats_cache.get(stripped, {})
            if not cached_stats:
                cached_stats = self._manifestation_stats_cache.get(
                    "the " + stripped, {}
                )

        # Resolve stats: entry_data (from lore parser) first, cache fallback
        resolved_move = entry_data.get("move") or cached_stats.get("move")
        resolved_health = entry_data.get("health") or cached_stats.get("health")
        resolved_save = entry_data.get("save") or cached_stats.get("save")
        resolved_banishment = entry_data.get("banishment") or cached_stats.get(
            "banishment"
        )

        # Resolve weapons/abilities: entry_data first, cache fallback
        entry_weapons = entry_data.get("weapons", [])
        entry_abilities = entry_data.get("abilities", [])
        resolved_weapons = (
            entry_weapons if entry_weapons else cached_stats.get("weapons", [])
        )
        resolved_abilities = (
            entry_abilities if entry_abilities else cached_stats.get("abilities", [])
        )
        weapons_json = json.dumps(resolved_weapons) if resolved_weapons else None
        abilities_json = json.dumps(resolved_abilities) if resolved_abilities else None

        statement = select(Manifestation).where(Manifestation.bsdata_id == bsdata_id)
        existing = self.session.execute(statement).scalars().first()

        if existing:
            existing.name = manif_name or existing.name
            existing.lore_id = lore_id
            existing.casting_value = entry_data.get("casting_value")
            existing.declare = entry_data.get("declare")
            existing.effect = entry_data.get("effect")
            existing.move = resolved_move or existing.move
            existing.health = resolved_health or existing.health
            existing.save = resolved_save or existing.save
            existing.banishment = resolved_banishment or existing.banishment
            if weapons_json:
                existing.weapons = weapons_json
            if abilities_json:
                existing.abilities = abilities_json
        else:
            manifestation = Manifestation(
                bsdata_id=bsdata_id,
                lore_id=lore_id,
                name=manif_name,
                casting_value=entry_data.get("casting_value"),
                declare=entry_data.get("declare"),
                effect=entry_data.get("effect"),
                move=resolved_move,
                health=resolved_health,
                save=resolved_save,
                banishment=resolved_banishment,
                weapons=weapons_json,
                abilities=abilities_json,
            )
            self.session.add(manifestation)

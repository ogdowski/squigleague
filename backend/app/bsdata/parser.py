"""BSData XML parser for Age of Sigmar 4th Edition catalog files."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

# BSData XML namespace
NS = {"bs": "http://www.battlescribe.net/schema/catalogueSchema"}
NS_GST = {"bs": "http://www.battlescribe.net/schema/gameSystemSchema"}

# Profile type IDs from BSData
PROFILE_TYPE_UNIT = "ff03-376e-972f-8ab2"
PROFILE_TYPE_MELEE = "9074-76b6-9e2f-81e3"
PROFILE_TYPE_RANGED = "1fd-a42f-41d3-fe05"
PROFILE_TYPE_ABILITY_PASSIVE = "907f-a48-6a04-f788"
PROFILE_TYPE_ABILITY_ACTIVATED = "59b6-d47a-a68a-5dcc"
PROFILE_TYPE_ABILITY_SPELL = "7312-8367-c171-f2ef"
PROFILE_TYPE_ABILITY_PRAYER = "5946-234-d7b4-6195"
PROFILE_TYPE_ABILITY_COMMAND = "55ac-f837-dded-5872"
PROFILE_TYPE_MANIFESTATION = "1287-3a-9799-7e40"
PROFILE_TYPE_BATTLE_TACTIC_CARD = "abf8-a239-9e66-54c1"

# Characteristic type IDs for Unit profile
CHAR_MOVE = "fed0-d1b3-1bb8-c501"
CHAR_HEALTH = "96be-54ae-ce7b-10b7"
CHAR_SAVE = "1981-ef09-96f6-7aa9"
CHAR_CONTROL = "6c6f-8510-9ce1-fc6e"

# Characteristic type IDs for Melee Weapon
CHAR_MELEE_ATK = "60e-35aa-31ed-e488"
CHAR_MELEE_HIT = "26dc-168-b2fd-cb93"
CHAR_MELEE_WND = "61c1-22cc-40af-2847"
CHAR_MELEE_RND = "eccc-10fa-6958-fb73"
CHAR_MELEE_DMG = "e948-9c71-12a6-6be4"
CHAR_MELEE_ABILITY = "eda3-7332-5db1-4159"

# Characteristic type IDs for Ranged Weapon
CHAR_RANGED_RNG = "c6b5-908c-a604-1a98"
CHAR_RANGED_ATK = "aa17-4296-2887-e05d"
CHAR_RANGED_HIT = "194d-aeb6-5ba7-83b4"
CHAR_RANGED_WND = "d3d5-9dc6-13de-8d1"
CHAR_RANGED_RND = "d03f-a9ae-3eec-755"
CHAR_RANGED_DMG = "96c2-d0a5-ea1e-653b"
CHAR_RANGED_ABILITY = "d793-3dd7-9c13-741e"

# Characteristic type IDs for Manifestation
CHAR_MANIF_MOVE = "c28a-6000-2a0b-e7cf"
CHAR_MANIF_HEALTH = "d1b9-3068-515-131e"
CHAR_MANIF_SAVE = "80c7-7691-b6ed-d6a6"
CHAR_MANIF_BANISHMENT = "97a2-d412-9ac-6a37"

# Characteristic type IDs for Battle Tactic Card
CHAR_TACTIC_CARD = "67f1-ce6d-1cf4-a4df"
CHAR_TACTIC_AFFRAY = "1047-3e43-674d-dc6c"
CHAR_TACTIC_STRIKE = "94d4-173e-0f65-c569"
CHAR_TACTIC_DOMINATION = "e1d7-1d3c-f001-62e0"

# Scourge of Ghyran publication ID
SOG_PUBLICATION_ID = "f894-7929-f79a-a269"

# Top-level faction-specific groups that map to artefacts
ARTEFACT_LIKE_GROUPS = {"Great Endrinworks", "Accursed Devices"}

# Top-level faction-specific groups that map to heroic traits
HEROIC_TRAIT_LIKE_GROUPS = {"Monstrous Traits", "Mount Traits", "Big Names", "Marks of"}

# Groups to skip (Path to Glory, internal)
SKIP_GROUPS = {"Battle Wounds + Scars", "Paths"}

# Grand Alliance mapping
GRAND_ALLIANCE_FACTIONS = {
    "Order": [
        "Cities of Sigmar",
        "Daughters of Khaine",
        "Fyreslayers",
        "Idoneth Deepkin",
        "Kharadron Overlords",
        "Lumineth Realm-lords",
        "Seraphon",
        "Stormcast Eternals",
        "Sylvaneth",
    ],
    "Chaos": [
        "Beasts of Chaos",
        "Blades of Khorne",
        "Disciples of Tzeentch",
        "Hedonites of Slaanesh",
        "Helsmiths of Hashut",
        "Maggotkin of Nurgle",
        "Skaven",
        "Slaves to Darkness",
    ],
    "Death": [
        "Flesh-eater Courts",
        "Nighthaunt",
        "Ossiarch Bonereapers",
        "Soulblight Gravelords",
    ],
    "Destruction": [
        "Bonesplitterz",
        "Gloomspite Gitz",
        "Ironjawz",
        "Kruleboyz",
        "Ogor Mawtribes",
        "Sons of Behemat",
    ],
}


def get_grand_alliance(faction_name: str) -> str:
    """Get grand alliance for a faction name."""
    for alliance, factions in GRAND_ALLIANCE_FACTIONS.items():
        if faction_name in factions:
            return alliance
    return "Unknown"


def clean_text(text: Optional[str]) -> Optional[str]:
    """Clean BSData text formatting (remove **^^...^^** markers)."""
    if not text:
        return None
    # Remove BSData markup like **^^HERO^^**
    cleaned = re.sub(r"\*\*\^\^([^*]+)\^\^\*\*", r"\1", text)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    return cleaned.strip()


def get_characteristic(profile: ET.Element, type_id: str, ns: dict) -> Optional[str]:
    """Get characteristic value by type ID."""
    for char in profile.findall(".//bs:characteristic", ns):
        if char.get("typeId") == type_id:
            return clean_text(char.text)
    # Also check by name attribute for older files
    return None


def get_characteristic_by_name(
    profile: ET.Element, name: str, ns: dict
) -> Optional[str]:
    """Get characteristic value by name.

    BSData sometimes uses mixed content in characteristics where the text
    comes after child elements (like conditionGroups). We use itertext()
    to get all text content.
    """
    for char in profile.findall(".//bs:characteristic", ns):
        if char.get("name") == name:
            # Use itertext() to get all text including after child elements
            all_text = "".join(char.itertext())
            return clean_text(all_text)
    return None


def _keywords_to_json(keywords_raw: Optional[str]) -> Optional[str]:
    """Convert raw keywords string (e.g. 'Blood Tithe, Spell') to JSON array string."""
    if not keywords_raw:
        return None
    keywords_list = [kw.strip() for kw in keywords_raw.split(",") if kw.strip()]
    if not keywords_list:
        return None
    return json.dumps(keywords_list)


def _extract_points(entry: ET.Element, ns: dict) -> Optional[int]:
    """Extract point cost from a selectionEntry's <costs> element."""
    for cost in entry.findall("bs:costs/bs:cost[@name='pts']", ns):
        try:
            value = int(float(cost.get("value", 0)))
            if value > 0:
                return value
        except (ValueError, TypeError):
            pass
    return None


class BSDataParser:
    """Parser for BSData XML catalog files."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def get_all_catalog_files(self) -> list[Path]:
        """Get all .cat files in the repository."""
        return list(self.repo_path.glob("*.cat"))

    def get_faction_catalogs(self) -> list[tuple[Path, Optional[Path]]]:
        """Get faction catalog pairs (main.cat, library.cat)."""
        catalogs = []
        for cat_file in self.get_all_catalog_files():
            name = cat_file.stem
            # Skip library files, RoR, Lores, Path to Glory
            if " - Library" in name:
                continue
            if name in ["Regiments of Renown", "Lores"]:
                continue
            if "Path to Glory" in name:
                continue
            # Skip LEGENDS factions
            if "[LEGENDS]" in name or name.startswith("þ"):
                continue

            # Find corresponding library file
            lib_file = self.repo_path / f"{name} - Library.cat"
            if lib_file.exists():
                catalogs.append((cat_file, lib_file))
            else:
                # Some factions don't have library files (subfactions)
                catalogs.append((cat_file, None))

        return catalogs

    def parse_game_system(self) -> dict:
        """Parse Age of Sigmar 4.0.gst for core content."""
        gst_file = self.repo_path / "Age of Sigmar 4.0.gst"
        if not gst_file.exists():
            return {}

        tree = ET.parse(gst_file)
        root = tree.getroot()

        result = {
            "manifestations": [],
            "battle_tactic_cards": [],
            "core_abilities": [],
        }

        # Parse manifestations with weapons and abilities from parent entries
        self._parse_manifestation_entries(root, NS_GST, result["manifestations"])

        # Parse battle tactic cards
        for profile in root.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_BATTLE_TACTIC_CARD),
            NS_GST,
        ):
            card = self._parse_battle_tactic_card(profile, NS_GST)
            if card:
                result["battle_tactic_cards"].append(card)

        # Parse core abilities (all types)
        core_ability_types = {
            PROFILE_TYPE_ABILITY_PASSIVE: "passive",
            PROFILE_TYPE_ABILITY_ACTIVATED: "activated",
            PROFILE_TYPE_ABILITY_COMMAND: "command",
        }
        for profile_type_id, ability_type in core_ability_types.items():
            for profile in root.findall(
                ".//bs:profile[@typeId='{}']".format(profile_type_id), NS_GST
            ):
                ability = self._parse_ability_profile(profile, NS_GST, ability_type)
                if ability:
                    result["core_abilities"].append(ability)

        return result

    def parse_catalog(self, cat_path: Path) -> dict:
        """Parse a single catalog file."""
        tree = ET.parse(cat_path)
        root = tree.getroot()

        catalog_name = root.get("name", cat_path.stem)
        catalog_id = root.get("id", "")

        return {
            "name": catalog_name,
            "bsdata_id": catalog_id,
            "file_path": str(cat_path),
        }

    def parse_library_catalog(self, lib_path: Path) -> dict:
        """Parse a library catalog for unit profiles, weapons, abilities."""
        tree = ET.parse(lib_path)
        root = tree.getroot()

        result = {
            "units": [],
            "manifestations": [],
        }

        for unit_entry in root.findall(".//bs:selectionEntry[@type='unit']", NS):
            # Check if this is a manifestation entry (has manifestation profile, no unit profile)
            has_manif_profile = (
                unit_entry.find(
                    ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_MANIFESTATION), NS
                )
                is not None
            )
            has_unit_profile = (
                unit_entry.find(
                    ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_UNIT), NS
                )
                is not None
            )

            if has_manif_profile and not has_unit_profile:
                manif = self._parse_library_manifestation_entry(unit_entry)
                if manif:
                    result["manifestations"].append(manif)
            else:
                unit = self._parse_unit_entry(unit_entry)
                if unit:
                    result["units"].append(unit)

        return result

    def _parse_library_manifestation_entry(self, entry: ET.Element) -> Optional[dict]:
        """Parse a manifestation selectionEntry from a Library.cat file.

        Extracts manifestation stats, weapons, and abilities.
        """
        entry_name = entry.get("name", "")

        manif_profile = entry.find(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_MANIFESTATION), NS
        )
        if manif_profile is None:
            return None

        manif = self._parse_manifestation_profile(manif_profile, NS)
        if not manif:
            return None

        # Use entry name (not profile name) for cache lookup
        manif["name"] = entry_name

        # Extract weapons
        weapons = []
        seen_ids = set()
        for weapon_profile in entry.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_MELEE), NS
        ):
            weapon = self._parse_weapon_profile(weapon_profile, NS, "melee")
            if weapon and weapon["bsdata_id"] not in seen_ids:
                weapons.append(weapon)
                seen_ids.add(weapon["bsdata_id"])
        for weapon_profile in entry.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_RANGED), NS
        ):
            weapon = self._parse_weapon_profile(weapon_profile, NS, "ranged")
            if weapon and weapon["bsdata_id"] not in seen_ids:
                weapons.append(weapon)
                seen_ids.add(weapon["bsdata_id"])

        # Extract abilities
        abilities = []
        ability_type_map = {
            PROFILE_TYPE_ABILITY_PASSIVE: "passive",
            PROFILE_TYPE_ABILITY_ACTIVATED: "activated",
        }
        for profile_type_id, ability_type in ability_type_map.items():
            for ability_profile in entry.findall(
                ".//bs:profile[@typeId='{}']".format(profile_type_id), NS
            ):
                ability = self._parse_ability_profile(ability_profile, NS, ability_type)
                if ability and ability["bsdata_id"] not in seen_ids:
                    abilities.append(ability)
                    seen_ids.add(ability["bsdata_id"])

        manif["weapons"] = weapons
        manif["abilities"] = abilities
        return manif

    def parse_faction_main_catalog(self, cat_path: Path) -> dict:
        """Parse main faction catalog for points costs, reinforcement, and notes."""
        tree = ET.parse(cat_path)
        root = tree.getroot()

        points_map = {}
        reinforced_units = set()
        notes_map = {}

        # Find all cost entries and battle profile metadata
        for entry in root.findall(".//bs:entryLink", NS):
            entry_name = entry.get("name", "")
            for cost in entry.findall(".//bs:cost[@name='pts']", NS):
                try:
                    points = int(float(cost.get("value", 0)))
                    if points > 0:
                        points_map[entry_name] = points
                except (ValueError, TypeError):
                    pass

            # Check for Reinforced child entryLink
            for child_link in entry.findall(".//bs:entryLink", NS):
                if child_link.get("name") == "Reinforced":
                    reinforced_units.add(entry_name)
                    break

            # Extract notes from error modifiers
            for modifier in entry.findall(".//bs:modifier", NS):
                if modifier.get("field") == "error" and modifier.get("type") == "add":
                    note_text = modifier.get("value", "")
                    if note_text and entry_name:
                        existing_notes = notes_map.get(entry_name, "")
                        if existing_notes:
                            notes_map[entry_name] = f"{existing_notes}\n{note_text}"
                        else:
                            notes_map[entry_name] = note_text

        for entry in root.findall(".//bs:selectionEntry", NS):
            entry_name = entry.get("name", "")
            for cost in entry.findall(".//bs:cost[@name='pts']", NS):
                try:
                    points = int(float(cost.get("value", 0)))
                    if points > 0:
                        points_map[entry_name] = points
                except (ValueError, TypeError):
                    pass

        # Parse battle traits from sharedSelectionEntries
        battle_traits = []
        for entry in root.findall("bs:sharedSelectionEntries/bs:selectionEntry", NS):
            entry_name = entry.get("name", "")
            if entry_name.startswith("Battle Traits"):
                for profile in entry.findall(".//bs:profile", NS):
                    trait = self._parse_ability_profile(profile, NS, "battle_trait")
                    if trait:
                        battle_traits.append(trait)

        # Parse heroic traits, artefacts, battle formations from sharedSelectionEntryGroups
        heroic_traits = []
        artefacts = []
        battle_formations = []
        spell_lore_refs = []
        prayer_lore_refs = []
        manifestation_lore_refs = []

        for group in root.findall(
            "bs:sharedSelectionEntryGroups/bs:selectionEntryGroup", NS
        ):
            group_name = group.get("name", "")

            if group_name == "Heroic Traits":
                heroic_traits.extend(
                    self._parse_enhancement_subgroups(group, NS, "heroic_trait")
                )

            elif group_name == "Artefacts of Power":
                artefacts.extend(
                    self._parse_enhancement_subgroups(group, NS, "artefact")
                )

            elif group_name.startswith("Battle Formations"):
                for entry in group.findall("bs:selectionEntries/bs:selectionEntry", NS):
                    formation = self._parse_battle_formation(entry, NS)
                    if formation:
                        battle_formations.append(formation)

            elif group_name == "Spell Lores":
                for entry in group.findall(".//bs:selectionEntry", NS):
                    lore_name = entry.get("name", "")
                    if not lore_name:
                        continue
                    entry_points = _extract_points(entry, NS)
                    for link in entry.findall("bs:entryLinks/bs:entryLink", NS):
                        target_id = link.get("targetId", "")
                        if target_id:
                            spell_lore_refs.append(
                                {
                                    "name": lore_name,
                                    "target_id": target_id,
                                    "points": entry_points,
                                }
                            )

            elif group_name == "Prayer Lores":
                for entry in group.findall(".//bs:selectionEntry", NS):
                    lore_name = entry.get("name", "")
                    if not lore_name:
                        continue
                    entry_points = _extract_points(entry, NS)
                    for link in entry.findall("bs:entryLinks/bs:entryLink", NS):
                        target_id = link.get("targetId", "")
                        if target_id:
                            prayer_lore_refs.append(
                                {
                                    "name": lore_name,
                                    "target_id": target_id,
                                    "points": entry_points,
                                }
                            )

            elif group_name == "Manifestation Lores":
                for entry in group.findall(".//bs:selectionEntry", NS):
                    lore_name = entry.get("name", "")
                    if not lore_name:
                        continue
                    for link in entry.findall("bs:entryLinks/bs:entryLink", NS):
                        target_id = link.get("targetId", "")
                        if target_id:
                            manifestation_lore_refs.append(
                                {"name": lore_name, "target_id": target_id}
                            )

            elif group_name not in SKIP_GROUPS:
                # Top-level faction-specific enhancement groups
                # (e.g., Great Endrinworks, Monstrous Traits, Big Names)
                is_artefact = any(
                    pattern in group_name for pattern in ARTEFACT_LIKE_GROUPS
                )
                is_heroic = any(
                    pattern in group_name for pattern in HEROIC_TRAIT_LIKE_GROUPS
                )

                if is_artefact:
                    artefacts.extend(
                        self._parse_enhancement_subgroups(group, NS, "artefact")
                    )
                elif is_heroic:
                    heroic_traits.extend(
                        self._parse_enhancement_subgroups(group, NS, "heroic_trait")
                    )

        # Parse unit entry links (for AoR catalogs that reference parent units)
        unit_refs = []
        for link in root.findall("bs:entryLinks/bs:entryLink", NS):
            link_type = link.get("type", "")
            target_id = link.get("targetId", "")
            link_name = link.get("name", "")
            if link_type == "selectionEntry" and target_id and link_name:
                unit_refs.append({"name": link_name, "target_id": target_id})

        return {
            "points": points_map,
            "reinforced_units": reinforced_units,
            "notes": notes_map,
            "battle_traits": battle_traits,
            "battle_formations": battle_formations,
            "heroic_traits": heroic_traits,
            "artefacts": artefacts,
            "spell_lore_refs": spell_lore_refs,
            "prayer_lore_refs": prayer_lore_refs,
            "manifestation_lore_refs": manifestation_lore_refs,
            "unit_refs": unit_refs,
        }

    def _parse_unit_entry(self, unit_entry: ET.Element) -> Optional[dict]:
        """Parse a complete unit selectionEntry including weapons and abilities."""
        entry_name = unit_entry.get("name", "")

        # Skip Anvil of Apotheosis (custom hero templates)
        if "Anvil of Apotheosis" in entry_name:
            return None

        # Skip Legends units
        for cat_link in unit_entry.findall(".//bs:categoryLink", NS):
            if cat_link.get("name") == "Legends":
                return None

        # Find the unit profile within this entry
        unit_profile = None
        for profile in unit_entry.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_UNIT), NS
        ):
            unit_profile = profile
            break

        if unit_profile is None:
            return None

        profile_id = unit_profile.get("id")
        if not profile_id:
            return None

        # Parse unit stats
        move = get_characteristic(
            unit_profile, CHAR_MOVE, NS
        ) or get_characteristic_by_name(unit_profile, "Move", NS)
        health_str = get_characteristic(
            unit_profile, CHAR_HEALTH, NS
        ) or get_characteristic_by_name(unit_profile, "Health", NS)
        save = get_characteristic(
            unit_profile, CHAR_SAVE, NS
        ) or get_characteristic_by_name(unit_profile, "Save", NS)
        control_str = get_characteristic(
            unit_profile, CHAR_CONTROL, NS
        ) or get_characteristic_by_name(unit_profile, "Control", NS)

        health = None
        if health_str:
            try:
                health = int(health_str)
            except ValueError:
                pass

        control = None
        if control_str:
            try:
                control = int(control_str)
            except ValueError:
                pass

        # Extract keywords from categoryLink elements
        keywords = []
        for cat_link in unit_entry.findall("bs:categoryLinks/bs:categoryLink", NS):
            keyword_name = cat_link.get("name", "")
            if keyword_name and keyword_name != "Legends":
                keywords.append(keyword_name)

        # Extract base_size and unit_size from model selectionEntry
        base_size = None
        unit_size = None
        for model_entry in unit_entry.findall(
            "bs:selectionEntries/bs:selectionEntry[@type='model']", NS
        ):
            # Base size from <rule name="Base Size"><description>
            for rule in model_entry.findall(".//bs:rule", NS):
                if rule.get("name") == "Base Size":
                    desc = rule.find("bs:description", NS)
                    if desc is not None and desc.text:
                        base_size = desc.text.strip()
                    break

            # Unit size from model constraint min value
            for constraint in model_entry.findall("bs:constraints/bs:constraint", NS):
                if constraint.get("type") == "min":
                    try:
                        unit_size = int(constraint.get("value", 0))
                    except (ValueError, TypeError):
                        pass
                    break
            break  # Only process first model entry

        # Find weapons throughout the unit entry (including nested selectionEntries)
        weapons = []
        seen_weapon_ids = set()

        # Melee weapons
        for weapon_profile in unit_entry.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_MELEE), NS
        ):
            weapon = self._parse_weapon_profile(weapon_profile, NS, "melee")
            if weapon and weapon["bsdata_id"] not in seen_weapon_ids:
                weapons.append(weapon)
                seen_weapon_ids.add(weapon["bsdata_id"])

        # Ranged weapons
        for weapon_profile in unit_entry.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_RANGED), NS
        ):
            weapon = self._parse_weapon_profile(weapon_profile, NS, "ranged")
            if weapon and weapon["bsdata_id"] not in seen_weapon_ids:
                weapons.append(weapon)
                seen_weapon_ids.add(weapon["bsdata_id"])

        # Find abilities throughout the unit entry (direct children and nested)
        abilities = []
        seen_ability_ids = set()

        ability_type_map = {
            PROFILE_TYPE_ABILITY_PASSIVE: "passive",
            PROFILE_TYPE_ABILITY_ACTIVATED: "activated",
            PROFILE_TYPE_ABILITY_SPELL: "spell",
            PROFILE_TYPE_ABILITY_PRAYER: "prayer",
            PROFILE_TYPE_ABILITY_COMMAND: "command",
        }

        for profile_type_id, ability_type in ability_type_map.items():
            for ability_profile in unit_entry.findall(
                ".//bs:profile[@typeId='{}']".format(profile_type_id), NS
            ):
                ability = self._parse_ability_profile(ability_profile, NS, ability_type)
                if ability and ability["bsdata_id"] not in seen_ability_ids:
                    abilities.append(ability)
                    seen_ability_ids.add(ability["bsdata_id"])

        return {
            "name": entry_name,
            "bsdata_id": profile_id,
            "move": move,
            "health": health,
            "save": save,
            "control": control,
            "keywords": keywords,
            "base_size": base_size,
            "unit_size": unit_size,
            "weapons": weapons,
            "abilities": abilities,
        }

    def _parse_weapon_profile(
        self, profile: ET.Element, ns: dict, weapon_type: str
    ) -> Optional[dict]:
        """Parse a weapon profile element."""
        name = profile.get("name")
        profile_id = profile.get("id")

        if not name or not profile_id:
            return None

        if weapon_type == "melee":
            attacks = get_characteristic(
                profile, CHAR_MELEE_ATK, ns
            ) or get_characteristic_by_name(profile, "Atk", ns)
            hit = get_characteristic(
                profile, CHAR_MELEE_HIT, ns
            ) or get_characteristic_by_name(profile, "Hit", ns)
            wound = get_characteristic(
                profile, CHAR_MELEE_WND, ns
            ) or get_characteristic_by_name(profile, "Wnd", ns)
            rend = get_characteristic(
                profile, CHAR_MELEE_RND, ns
            ) or get_characteristic_by_name(profile, "Rnd", ns)
            damage = get_characteristic(
                profile, CHAR_MELEE_DMG, ns
            ) or get_characteristic_by_name(profile, "Dmg", ns)
            ability = get_characteristic(
                profile, CHAR_MELEE_ABILITY, ns
            ) or get_characteristic_by_name(profile, "Ability", ns)
            rng = None
        else:
            rng = get_characteristic(
                profile, CHAR_RANGED_RNG, ns
            ) or get_characteristic_by_name(profile, "Rng", ns)
            attacks = get_characteristic(
                profile, CHAR_RANGED_ATK, ns
            ) or get_characteristic_by_name(profile, "Atk", ns)
            hit = get_characteristic(
                profile, CHAR_RANGED_HIT, ns
            ) or get_characteristic_by_name(profile, "Hit", ns)
            wound = get_characteristic(
                profile, CHAR_RANGED_WND, ns
            ) or get_characteristic_by_name(profile, "Wnd", ns)
            rend = get_characteristic(
                profile, CHAR_RANGED_RND, ns
            ) or get_characteristic_by_name(profile, "Rnd", ns)
            damage = get_characteristic(
                profile, CHAR_RANGED_DMG, ns
            ) or get_characteristic_by_name(profile, "Dmg", ns)
            ability = get_characteristic(
                profile, CHAR_RANGED_ABILITY, ns
            ) or get_characteristic_by_name(profile, "Ability", ns)

        return {
            "name": name,
            "bsdata_id": profile_id,
            "weapon_type": weapon_type,
            "range": rng,
            "attacks": attacks,
            "hit": hit,
            "wound": wound,
            "rend": rend,
            "damage": damage,
            "ability": ability,
        }

    def _parse_ability_profile(
        self, profile: ET.Element, ns: dict, ability_type: str
    ) -> Optional[dict]:
        """Parse an ability profile element."""
        name = profile.get("name")
        profile_id = profile.get("id")

        if not name or not profile_id:
            return None

        effect = get_characteristic_by_name(profile, "Effect", ns)
        keywords_raw = get_characteristic_by_name(profile, "Keywords", ns)
        keywords_json = _keywords_to_json(keywords_raw)
        timing = get_characteristic_by_name(profile, "Timing", ns)
        declare = get_characteristic_by_name(profile, "Declare", ns)

        # Extract Color from attributes (uses same namespace prefix)
        color = None
        ns_prefix = list(ns.keys())[0]
        ns_uri = ns[ns_prefix]
        for attr in profile.findall(f"{{{ns_uri}}}attributes/{{{ns_uri}}}attribute"):
            if attr.get("name") == "Color" and attr.text:
                color = attr.text.strip()
                break

        return {
            "name": name,
            "bsdata_id": profile_id,
            "ability_type": ability_type,
            "effect": effect,
            "keywords": keywords_json,
            "timing": timing,
            "declare": declare,
            "color": color,
        }

    def _parse_enhancement_subgroups(
        self, parent_group: ET.Element, ns: dict, ability_type: str
    ) -> list[dict]:
        """Parse enhancement entries from subgroups, capturing group_name and seasonal flag.

        Iterates child selectionEntryGroup elements within a parent group,
        parses ability profiles from each, and tags with the subgroup name.
        Also handles direct selectionEntry children (no subgroup).
        """
        results = []

        # Iterate child selectionEntryGroup elements
        for sub_group in parent_group.findall(
            "bs:selectionEntryGroups/bs:selectionEntryGroup", ns
        ):
            sub_group_name = sub_group.get("name", "")
            sub_pub_id = sub_group.get("publicationId", "")
            is_seasonal = sub_pub_id == SOG_PUBLICATION_ID

            for entry in sub_group.findall(".//bs:selectionEntry", ns):
                entry_points = _extract_points(entry, ns)
                # Check entry-level publicationId too
                entry_pub_id = entry.get("publicationId", "")
                entry_seasonal = is_seasonal or entry_pub_id == SOG_PUBLICATION_ID

                for profile in entry.findall(".//bs:profile", ns):
                    parsed = self._parse_ability_profile(profile, ns, ability_type)
                    if parsed:
                        parsed["points"] = entry_points
                        parsed["group_name"] = sub_group_name
                        parsed["is_seasonal"] = entry_seasonal
                        results.append(parsed)

        # Also check for direct selectionEntry children (no subgroup)
        for entry in parent_group.findall("bs:selectionEntries/bs:selectionEntry", ns):
            entry_points = _extract_points(entry, ns)
            entry_pub_id = entry.get("publicationId", "")
            entry_seasonal = entry_pub_id == SOG_PUBLICATION_ID

            for profile in entry.findall(".//bs:profile", ns):
                parsed = self._parse_ability_profile(profile, ns, ability_type)
                if parsed:
                    parsed["points"] = entry_points
                    parsed["group_name"] = parent_group.get("name", "")
                    parsed["is_seasonal"] = entry_seasonal
                    results.append(parsed)

        return results

    def _parse_battle_formation(self, entry: ET.Element, ns: dict) -> Optional[dict]:
        """Parse a battle formation selectionEntry."""
        formation_name = entry.get("name", "")
        formation_id = entry.get("id", "")

        if not formation_name or not formation_id:
            return None

        points = _extract_points(entry, ns)

        # Find the first ability profile inside
        ability_data = None
        for profile in entry.findall(".//bs:profile", ns):
            ability_data = self._parse_ability_profile(profile, ns, "formation")
            if ability_data:
                break

        result = {
            "name": formation_name,
            "bsdata_id": formation_id,
            "points": points,
        }

        if ability_data:
            result["ability_name"] = ability_data["name"]
            result["ability_type"] = ability_data["ability_type"]
            result["effect"] = ability_data["effect"]
            result["timing"] = ability_data["timing"]
            result["declare"] = ability_data["declare"]
            result["color"] = ability_data["color"]
            result["keywords"] = ability_data["keywords"]

        return result

    def _parse_manifestation_entries(self, root: ET.Element, ns: dict, output: list):
        """Find selectionEntries containing manifestation profiles and extract weapons/abilities."""
        ns_uri = ns[list(ns.keys())[0]]

        # Build parent map so we can walk up from profiles to selectionEntries
        parent_map = {}
        for parent in root.iter():
            for child in parent:
                parent_map[child] = parent

        # Find all manifestation profiles
        for profile in root.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_MANIFESTATION), ns
        ):
            manif = self._parse_manifestation_profile(profile, ns)
            if not manif:
                continue

            # Walk up to find the parent selectionEntry
            entry = profile
            while entry is not None:
                tag_local = entry.tag.split("}")[-1] if "}" in entry.tag else entry.tag
                if tag_local == "selectionEntry":
                    break
                entry = parent_map.get(entry)

            # Extract weapons and abilities from the selectionEntry
            weapons = []
            abilities = []

            if entry is not None:
                seen_ids = set()

                for weapon_profile in entry.findall(
                    ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_MELEE), ns
                ):
                    weapon = self._parse_weapon_profile(weapon_profile, ns, "melee")
                    if weapon and weapon["bsdata_id"] not in seen_ids:
                        weapons.append(weapon)
                        seen_ids.add(weapon["bsdata_id"])

                for weapon_profile in entry.findall(
                    ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_RANGED), ns
                ):
                    weapon = self._parse_weapon_profile(weapon_profile, ns, "ranged")
                    if weapon and weapon["bsdata_id"] not in seen_ids:
                        weapons.append(weapon)
                        seen_ids.add(weapon["bsdata_id"])

                ability_type_map = {
                    PROFILE_TYPE_ABILITY_PASSIVE: "passive",
                    PROFILE_TYPE_ABILITY_ACTIVATED: "activated",
                }
                for profile_type_id, ability_type in ability_type_map.items():
                    for ability_profile in entry.findall(
                        ".//bs:profile[@typeId='{}']".format(profile_type_id), ns
                    ):
                        ability = self._parse_ability_profile(
                            ability_profile, ns, ability_type
                        )
                        if ability and ability["bsdata_id"] not in seen_ids:
                            abilities.append(ability)
                            seen_ids.add(ability["bsdata_id"])

            manif["weapons"] = weapons
            manif["abilities"] = abilities
            output.append(manif)

    def _parse_manifestation_profile(
        self, profile: ET.Element, ns: dict
    ) -> Optional[dict]:
        """Parse a manifestation profile element."""
        name = profile.get("name")
        profile_id = profile.get("id")

        if not name or not profile_id:
            return None

        move = get_characteristic(
            profile, CHAR_MANIF_MOVE, ns
        ) or get_characteristic_by_name(profile, "Move", ns)
        health_str = get_characteristic(
            profile, CHAR_MANIF_HEALTH, ns
        ) or get_characteristic_by_name(profile, "Health", ns)
        save = get_characteristic(
            profile, CHAR_MANIF_SAVE, ns
        ) or get_characteristic_by_name(profile, "Save", ns)
        banishment = get_characteristic(
            profile, CHAR_MANIF_BANISHMENT, ns
        ) or get_characteristic_by_name(profile, "Banishment", ns)

        health = None
        if health_str:
            try:
                health = int(health_str)
            except ValueError:
                pass

        return {
            "name": name,
            "bsdata_id": profile_id,
            "move": move,
            "health": health,
            "save": save,
            "banishment": banishment,
        }

    def _parse_battle_tactic_card(
        self, profile: ET.Element, ns: dict
    ) -> Optional[dict]:
        """Parse a battle tactic card profile."""
        name = profile.get("name")
        profile_id = profile.get("id")

        if not name or not profile_id:
            return None

        card_rules = get_characteristic(
            profile, CHAR_TACTIC_CARD, ns
        ) or get_characteristic_by_name(profile, "Card", ns)
        affray = get_characteristic(
            profile, CHAR_TACTIC_AFFRAY, ns
        ) or get_characteristic_by_name(profile, "Affray", ns)
        strike = get_characteristic(
            profile, CHAR_TACTIC_STRIKE, ns
        ) or get_characteristic_by_name(profile, "Strike", ns)
        domination = get_characteristic(
            profile, CHAR_TACTIC_DOMINATION, ns
        ) or get_characteristic_by_name(profile, "Domination", ns)

        # Parse affray/strike/domination into name and effect
        def parse_tactic(text: Optional[str]) -> tuple[Optional[str], Optional[str]]:
            if not text:
                return None, None
            # Format: "Name:\nEffect" or "Name: Effect"
            parts = text.split(":", 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
            return None, text

        affray_name, affray_effect = parse_tactic(affray)
        strike_name, strike_effect = parse_tactic(strike)
        domination_name, domination_effect = parse_tactic(domination)

        return {
            "name": name,
            "bsdata_id": profile_id,
            "card_rules": card_rules,
            "affray_name": affray_name,
            "affray_effect": affray_effect,
            "strike_name": strike_name,
            "strike_effect": strike_effect,
            "domination_name": domination_name,
            "domination_effect": domination_effect,
        }

    def parse_regiments_of_renown(self) -> list[dict]:
        """Parse Regiments of Renown catalog."""
        ror_file = self.repo_path / "Regiments of Renown.cat"
        if not ror_file.exists():
            return []

        tree = ET.parse(ror_file)
        root = tree.getroot()

        regiments = []

        for entry in root.findall(".//bs:selectionEntry[@type='upgrade']", NS):
            name = entry.get("name", "")
            entry_id = entry.get("id", "")

            if not name or not entry_id:
                continue

            # Get points
            points = None
            for cost in entry.findall(".//bs:cost[@name='pts']", NS):
                try:
                    points = int(float(cost.get("value", 0)))
                except (ValueError, TypeError):
                    pass

            # Get description from infoLinks or rules
            description = None
            for rule in entry.findall(".//bs:rule", NS):
                desc = rule.find("bs:description", NS)
                if desc is not None and desc.text:
                    description = clean_text(desc.text)
                    break

            regiments.append(
                {
                    "name": name,
                    "bsdata_id": entry_id,
                    "points": points,
                    "description": description,
                }
            )

        return regiments

    def parse_lores(self) -> dict:
        """Parse Lores.cat for spell lores."""
        lores_file = self.repo_path / "Lores.cat"
        if not lores_file.exists():
            return {"spell_lores": []}

        tree = ET.parse(lores_file)
        root = tree.getroot()

        spell_lores = []

        for entry in root.findall(".//bs:selectionEntryGroup", NS):
            lore_name = entry.get("name", "")
            lore_id = entry.get("id", "")

            if "Lore" not in lore_name:
                continue

            spells = []
            for spell_profile in entry.findall(
                ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_ABILITY_SPELL), NS
            ):
                spell = self._parse_spell_profile(spell_profile)
                if spell:
                    spells.append(spell)

            if spells:
                spell_lores.append(
                    {
                        "name": lore_name,
                        "bsdata_id": lore_id,
                        "spells": spells,
                    }
                )

        return {"spell_lores": spell_lores}

    def parse_lores_indexed(self) -> dict:
        """Parse Lores.cat and return dict indexed by selectionEntryGroup ID.

        This allows cross-referencing from faction main catalogs which use
        entryLink targetId to reference lore groups in Lores.cat.
        """
        lores_file = self.repo_path / "Lores.cat"
        if not lores_file.exists():
            return {}

        tree = ET.parse(lores_file)
        root = tree.getroot()

        index = {}

        for group in root.findall(".//bs:selectionEntryGroup", NS):
            group_id = group.get("id", "")
            group_name = group.get("name", "")
            if not group_id:
                continue

            entries = []

            # Iterate selectionEntries to capture all profiles per entry
            selection_entries = group.findall(".//bs:selectionEntry", NS)

            if selection_entries:
                for sel_entry in selection_entries:
                    entry = self._parse_lore_selection_entry(sel_entry)
                    if entry:
                        entries.append(entry)
            else:
                # Fallback: iterate profiles directly (flat structure)
                for profile in group.findall(".//bs:profile", NS):
                    profile_type_id = profile.get("typeId", "")
                    if profile_type_id == PROFILE_TYPE_ABILITY_SPELL:
                        parsed = self._parse_spell_profile(profile)
                        if parsed:
                            entries.append(parsed)
                    elif profile_type_id == PROFILE_TYPE_ABILITY_PRAYER:
                        parsed = self._parse_prayer_profile(profile)
                        if parsed:
                            entries.append(parsed)

            if entries:
                index[group_id] = {
                    "name": group_name,
                    "entries": entries,
                }

        return index

    def parse_universal_manifestation_lores(self) -> list:
        """Parse the master 'Manifestation Lores' shared group from Lores.cat.

        Returns a list of universal lore dicts with name, bsdata_id, points,
        and target_id (pointing to the actual lore group in the lores index).
        """
        lores_file = self.repo_path / "Lores.cat"
        if not lores_file.exists():
            return []

        tree = ET.parse(lores_file)
        root = tree.getroot()

        result = []

        # Find the shared "Manifestation Lores" group
        for group in root.findall(
            "bs:sharedSelectionEntryGroups/bs:selectionEntryGroup", NS
        ):
            if group.get("name") != "Manifestation Lores":
                continue

            for entry in group.findall("bs:selectionEntries/bs:selectionEntry", NS):
                lore_name = entry.get("name", "")
                lore_id = entry.get("id", "")

                # Extract points cost
                points = None
                for cost in entry.findall(".//bs:cost", NS):
                    cost_value = cost.get("value", "0")
                    try:
                        parsed_points = int(float(cost_value))
                        if parsed_points > 0:
                            points = parsed_points
                    except (ValueError, TypeError):
                        pass

                # Get the target lore group ID via entryLink
                target_id = None
                for link in entry.findall("bs:entryLinks/bs:entryLink", NS):
                    target_id = link.get("targetId")
                    break

                if lore_name and target_id:
                    result.append(
                        {
                            "name": lore_name,
                            "bsdata_id": lore_id,
                            "points": points,
                            "target_id": target_id,
                        }
                    )

        return result

    def _parse_lore_selection_entry(self, sel_entry: ET.Element) -> Optional[dict]:
        """Parse a lore selectionEntry, extracting the summoning spell plus
        any manifestation stats, weapons, and abilities from sibling profiles."""
        entry = None

        # Find the primary spell/prayer profile (summoning ability)
        for profile in sel_entry.findall(".//bs:profile", NS):
            profile_type_id = profile.get("typeId", "")
            if profile_type_id == PROFILE_TYPE_ABILITY_SPELL:
                entry = self._parse_spell_profile(profile)
                break
            elif profile_type_id == PROFILE_TYPE_ABILITY_PRAYER:
                entry = self._parse_prayer_profile(profile)
                break

        if not entry:
            return None

        # Extract manifestation stats from sibling profile
        for profile in sel_entry.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_MANIFESTATION), NS
        ):
            manif = self._parse_manifestation_profile(profile, NS)
            if manif:
                entry["move"] = manif.get("move")
                entry["health"] = manif.get("health")
                entry["save"] = manif.get("save")
                entry["banishment"] = manif.get("banishment")
                break

        # Extract weapons
        weapons = []
        seen_ids = set()
        for wp in sel_entry.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_MELEE), NS
        ):
            weapon = self._parse_weapon_profile(wp, NS, "melee")
            if weapon and weapon["bsdata_id"] not in seen_ids:
                weapons.append(weapon)
                seen_ids.add(weapon["bsdata_id"])
        for wp in sel_entry.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_RANGED), NS
        ):
            weapon = self._parse_weapon_profile(wp, NS, "ranged")
            if weapon and weapon["bsdata_id"] not in seen_ids:
                weapons.append(weapon)
                seen_ids.add(weapon["bsdata_id"])

        # Extract abilities
        abilities = []
        ability_type_map = {
            PROFILE_TYPE_ABILITY_PASSIVE: "passive",
            PROFILE_TYPE_ABILITY_ACTIVATED: "activated",
        }
        for profile_type_id, ability_type in ability_type_map.items():
            for ap in sel_entry.findall(
                ".//bs:profile[@typeId='{}']".format(profile_type_id), NS
            ):
                ability = self._parse_ability_profile(ap, NS, ability_type)
                if ability and ability["bsdata_id"] not in seen_ids:
                    abilities.append(ability)
                    seen_ids.add(ability["bsdata_id"])

        if weapons:
            entry["weapons"] = weapons
        if abilities:
            entry["abilities"] = abilities

        return entry

    def _parse_prayer_profile(self, profile: ET.Element) -> Optional[dict]:
        """Parse a prayer profile (same structure as spell, uses Chanting Value)."""
        name = profile.get("name")
        profile_id = profile.get("id")

        if not name or not profile_id:
            return None

        chanting_value = get_characteristic_by_name(profile, "Chanting Value", NS)
        declare = get_characteristic_by_name(profile, "Declare", NS)
        effect = get_characteristic_by_name(profile, "Effect", NS)
        keywords_raw = get_characteristic_by_name(profile, "Keywords", NS)

        return {
            "name": name,
            "bsdata_id": profile_id,
            "casting_value": chanting_value,
            "declare": declare,
            "effect": effect,
            "keywords": _keywords_to_json(keywords_raw),
        }

    def _parse_spell_profile(self, profile: ET.Element) -> Optional[dict]:
        """Parse a spell profile."""
        name = profile.get("name")
        profile_id = profile.get("id")

        if not name or not profile_id:
            return None

        casting_value = get_characteristic_by_name(profile, "Casting Value", NS)
        declare = get_characteristic_by_name(profile, "Declare", NS)
        effect = get_characteristic_by_name(profile, "Effect", NS)
        keywords_raw = get_characteristic_by_name(profile, "Keywords", NS)

        return {
            "name": name,
            "bsdata_id": profile_id,
            "casting_value": casting_value,
            "declare": declare,
            "effect": effect,
            "keywords": _keywords_to_json(keywords_raw),
        }

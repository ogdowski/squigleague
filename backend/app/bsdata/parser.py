"""BSData XML parser for Age of Sigmar 4th Edition catalog files."""

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

        # Parse manifestations
        for profile in root.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_MANIFESTATION), NS_GST
        ):
            manif = self._parse_manifestation_profile(profile, NS_GST)
            if manif:
                result["manifestations"].append(manif)

        # Parse battle tactic cards
        for profile in root.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_BATTLE_TACTIC_CARD),
            NS_GST,
        ):
            card = self._parse_battle_tactic_card(profile, NS_GST)
            if card:
                result["battle_tactic_cards"].append(card)

        # Parse core abilities (passive)
        for profile in root.findall(
            ".//bs:profile[@typeId='{}']".format(PROFILE_TYPE_ABILITY_PASSIVE), NS_GST
        ):
            ability = self._parse_ability_profile(profile, NS_GST, "passive")
            if ability and ability.get("name") in ["Fly", "Ward Save", "Guarded Hero"]:
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
        }

        # Find unit selectionEntries (type="unit") and parse them completely
        for unit_entry in root.findall(".//bs:selectionEntry[@type='unit']", NS):
            unit = self._parse_unit_entry(unit_entry)
            if unit:
                result["units"].append(unit)

        return result

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

        # Parse heroic traits and artefacts from sharedSelectionEntryGroups
        heroic_traits = []
        artefacts = []
        spell_lore_refs = []
        prayer_lore_refs = []
        manifestation_lore_refs = []

        for group in root.findall(
            "bs:sharedSelectionEntryGroups/bs:selectionEntryGroup", NS
        ):
            group_name = group.get("name", "")

            if group_name == "Heroic Traits":
                for profile in group.findall(".//bs:profile", NS):
                    trait = self._parse_ability_profile(profile, NS, "heroic_trait")
                    if trait:
                        heroic_traits.append(trait)

            elif group_name == "Artefacts of Power":
                for profile in group.findall(".//bs:profile", NS):
                    artefact = self._parse_ability_profile(profile, NS, "artefact")
                    if artefact:
                        artefacts.append(artefact)

            elif group_name == "Spell Lores":
                for entry in group.findall(".//bs:selectionEntry", NS):
                    lore_name = entry.get("name", "")
                    if not lore_name:
                        continue
                    for link in entry.findall("bs:entryLinks/bs:entryLink", NS):
                        target_id = link.get("targetId", "")
                        if target_id:
                            spell_lore_refs.append(
                                {"name": lore_name, "target_id": target_id}
                            )

            elif group_name == "Prayer Lores":
                for entry in group.findall(".//bs:selectionEntry", NS):
                    lore_name = entry.get("name", "")
                    if not lore_name:
                        continue
                    for link in entry.findall("bs:entryLinks/bs:entryLink", NS):
                        target_id = link.get("targetId", "")
                        if target_id:
                            prayer_lore_refs.append(
                                {"name": lore_name, "target_id": target_id}
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

        return {
            "points": points_map,
            "reinforced_units": reinforced_units,
            "notes": notes_map,
            "battle_traits": battle_traits,
            "heroic_traits": heroic_traits,
            "artefacts": artefacts,
            "spell_lore_refs": spell_lore_refs,
            "prayer_lore_refs": prayer_lore_refs,
            "manifestation_lore_refs": manifestation_lore_refs,
        }

    def _parse_unit_entry(self, unit_entry: ET.Element) -> Optional[dict]:
        """Parse a complete unit selectionEntry including weapons and abilities."""
        entry_name = unit_entry.get("name", "")

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
        keywords = get_characteristic_by_name(profile, "Keywords", ns)
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
            "keywords": keywords,
            "timing": timing,
            "declare": declare,
            "color": color,
        }

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

    def _parse_prayer_profile(self, profile: ET.Element) -> Optional[dict]:
        """Parse a prayer profile (same structure as spell, uses Chanting Value)."""
        name = profile.get("name")
        profile_id = profile.get("id")

        if not name or not profile_id:
            return None

        chanting_value = get_characteristic_by_name(profile, "Chanting Value", NS)
        effect = get_characteristic_by_name(profile, "Effect", NS)

        return {
            "name": name,
            "bsdata_id": profile_id,
            "casting_value": chanting_value,
            "effect": effect,
        }

    def _parse_spell_profile(self, profile: ET.Element) -> Optional[dict]:
        """Parse a spell profile."""
        name = profile.get("name")
        profile_id = profile.get("id")

        if not name or not profile_id:
            return None

        casting_value = get_characteristic_by_name(profile, "Casting Value", NS)
        effect = get_characteristic_by_name(profile, "Effect", NS)

        return {
            "name": name,
            "bsdata_id": profile_id,
            "casting_value": casting_value,
            "effect": effect,
        }

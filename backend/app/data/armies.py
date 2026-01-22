"""Army faction data and detection for Age of Sigmar."""

# Age of Sigmar 4th Edition army factions
ARMY_FACTIONS = [
    # Order
    "Cities of Sigmar",
    "Daughters of Khaine",
    "Fyreslayers",
    "Idoneth Deepkin",
    "Kharadron Overlords",
    "Lumineth Realm-lords",
    "Seraphon",
    "Stormcast Eternals",
    "Sylvaneth",
    # Chaos
    "Blades of Khorne",
    "Disciples of Tzeentch",
    "Hedonites of Slaanesh",
    "Helsmiths of Hashut",
    "Maggotkin of Nurgle",
    "Skaven",
    "Slaves to Darkness",
    # Death
    "Flesh-eater Courts",
    "Nighthaunt",
    "Ossiarch Bonereapers",
    "Soulblight Gravelords",
    # Destruction
    "Gloomspite Gitz",
    "Ironjawz",
    "Kruleboyz",
    "Ogor Mawtribes",
    "Sons of Behemat",
]

# Keywords/patterns to detect army factions from list text
# Maps lowercase keywords to faction names
ARMY_DETECTION_PATTERNS = {
    # Order
    "cities of sigmar": "Cities of Sigmar",
    "freeguild": "Cities of Sigmar",
    "collegiate arcane": "Cities of Sigmar",
    "ironweld": "Cities of Sigmar",
    "daughters of khaine": "Daughters of Khaine",
    "khainite": "Daughters of Khaine",
    "melusai": "Daughters of Khaine",
    "witch aelf": "Daughters of Khaine",
    "hag queen": "Daughters of Khaine",
    "morathi": "Daughters of Khaine",
    "fyreslayers": "Fyreslayers",
    "fyreslayer": "Fyreslayers",
    "vulkite": "Fyreslayers",
    "hearthguard": "Fyreslayers",
    "auric": "Fyreslayers",
    "magmadroth": "Fyreslayers",
    "idoneth deepkin": "Idoneth Deepkin",
    "idoneth": "Idoneth Deepkin",
    "akhelian": "Idoneth Deepkin",
    "namarti": "Idoneth Deepkin",
    "isharann": "Idoneth Deepkin",
    "kharadron overlords": "Kharadron Overlords",
    "kharadron": "Kharadron Overlords",
    "arkanaut": "Kharadron Overlords",
    "grundstok": "Kharadron Overlords",
    "endrinmaster": "Kharadron Overlords",
    "lumineth realm-lords": "Lumineth Realm-lords",
    "lumineth": "Lumineth Realm-lords",
    "vanari": "Lumineth Realm-lords",
    "alarith": "Lumineth Realm-lords",
    "hurakan": "Lumineth Realm-lords",
    "scinari": "Lumineth Realm-lords",
    "teclis": "Lumineth Realm-lords",
    "seraphon": "Seraphon",
    "saurus": "Seraphon",
    "skink": "Seraphon",
    "slann": "Seraphon",
    "kroxigor": "Seraphon",
    "stormcast eternals": "Stormcast Eternals",
    "stormcast": "Stormcast Eternals",
    "liberator": "Stormcast Eternals",
    "retributor": "Stormcast Eternals",
    "sequitor": "Stormcast Eternals",
    "evocator": "Stormcast Eternals",
    "lord-celestant": "Stormcast Eternals",
    "knight-incantor": "Stormcast Eternals",
    "sylvaneth": "Sylvaneth",
    "dryad": "Sylvaneth",
    "treelord": "Sylvaneth",
    "kurnoth": "Sylvaneth",
    "alarielle": "Sylvaneth",
    "tree-revenant": "Sylvaneth",
    # Chaos
    "blades of khorne": "Blades of Khorne",
    "khorne": "Blades of Khorne",
    "bloodthirster": "Blades of Khorne",
    "bloodletter": "Blades of Khorne",
    "bloodreaver": "Blades of Khorne",
    "skullgrinder": "Blades of Khorne",
    "slaughterpriest": "Blades of Khorne",
    "disciples of tzeentch": "Disciples of Tzeentch",
    "tzeentch": "Disciples of Tzeentch",
    "horror": "Disciples of Tzeentch",
    "tzaangor": "Disciples of Tzeentch",
    "lord of change": "Disciples of Tzeentch",
    "gaunt summoner": "Disciples of Tzeentch",
    "hedonites of slaanesh": "Hedonites of Slaanesh",
    "slaanesh": "Hedonites of Slaanesh",
    "daemonette": "Hedonites of Slaanesh",
    "keeper of secrets": "Hedonites of Slaanesh",
    "syll'esske": "Hedonites of Slaanesh",
    "sigvald": "Hedonites of Slaanesh",
    "helsmiths of hashut": "Helsmiths of Hashut",
    "hashut": "Helsmiths of Hashut",
    "chaos dwarf": "Helsmiths of Hashut",
    "k'daai": "Helsmiths of Hashut",
    "maggotkin of nurgle": "Maggotkin of Nurgle",
    "nurgle": "Maggotkin of Nurgle",
    "plaguebearer": "Maggotkin of Nurgle",
    "putrid blightking": "Maggotkin of Nurgle",
    "great unclean one": "Maggotkin of Nurgle",
    "lord of afflictions": "Maggotkin of Nurgle",
    "skaven": "Skaven",
    "clanrat": "Skaven",
    "stormvermin": "Skaven",
    "grey seer": "Skaven",
    "verminlord": "Skaven",
    "skryre": "Skaven",
    "pestilens": "Skaven",
    "moulder": "Skaven",
    "slaves to darkness": "Slaves to Darkness",
    "chaos warrior": "Slaves to Darkness",
    "chaos knight": "Slaves to Darkness",
    "varanguard": "Slaves to Darkness",
    "chaos lord": "Slaves to Darkness",
    "archaon": "Slaves to Darkness",
    "darkoath": "Slaves to Darkness",
    # Death
    "flesh-eater courts": "Flesh-eater Courts",
    "flesh-eater": "Flesh-eater Courts",
    "abhorrant": "Flesh-eater Courts",
    "crypt ghoul": "Flesh-eater Courts",
    "crypt horror": "Flesh-eater Courts",
    "zombie dragon": "Flesh-eater Courts",
    "nighthaunt": "Nighthaunt",
    "chainrasp": "Nighthaunt",
    "spirit host": "Nighthaunt",
    "grimghast": "Nighthaunt",
    "bladegheist": "Nighthaunt",
    "lady olynder": "Nighthaunt",
    "ossiarch bonereapers": "Ossiarch Bonereapers",
    "ossiarch": "Ossiarch Bonereapers",
    "mortek": "Ossiarch Bonereapers",
    "kavalos": "Ossiarch Bonereapers",
    "nagash": "Ossiarch Bonereapers",
    "katakros": "Ossiarch Bonereapers",
    "soulblight gravelords": "Soulblight Gravelords",
    "soulblight": "Soulblight Gravelords",
    "vampire": "Soulblight Gravelords",
    "blood knight": "Soulblight Gravelords",
    "skeleton": "Soulblight Gravelords",
    "zombie": "Soulblight Gravelords",
    "vargheist": "Soulblight Gravelords",
    "mannfred": "Soulblight Gravelords",
    "neferata": "Soulblight Gravelords",
    # Destruction
    "gloomspite gitz": "Gloomspite Gitz",
    "gloomspite": "Gloomspite Gitz",
    "grot": "Gloomspite Gitz",
    "squig": "Gloomspite Gitz",
    "troggoth": "Gloomspite Gitz",
    "spider rider": "Gloomspite Gitz",
    "loonboss": "Gloomspite Gitz",
    "ironjawz": "Ironjawz",
    "ironjaw": "Ironjawz",
    "brute": "Ironjawz",
    "gore-grunta": "Ironjawz",
    "megaboss": "Ironjawz",
    "maw-krusha": "Ironjawz",
    "gordrakk": "Ironjawz",
    "kruleboyz": "Kruleboyz",
    "kruleboy": "Kruleboyz",
    "gutrippaz": "Kruleboyz",
    "hobgrot": "Kruleboyz",
    "killaboss": "Kruleboyz",
    "swampcalla": "Kruleboyz",
    "ogor mawtribes": "Ogor Mawtribes",
    "ogor": "Ogor Mawtribes",
    "glutton": "Ogor Mawtribes",
    "irongut": "Ogor Mawtribes",
    "leadbelcher": "Ogor Mawtribes",
    "stonehorn": "Ogor Mawtribes",
    "thundertusk": "Ogor Mawtribes",
    "sons of behemat": "Sons of Behemat",
    "mega-gargant": "Sons of Behemat",
    "gargant": "Sons of Behemat",
    "mancrusher": "Sons of Behemat",
}


def detect_army_faction(army_list_text: str, max_lines: int = 10) -> str | None:
    """
    Detect army faction from the first N lines of an army list.

    Args:
        army_list_text: The full army list text
        max_lines: Number of lines from the beginning to analyze (default 10)

    Returns:
        Detected faction name or None if not detected
    """
    if not army_list_text:
        return None

    # Get first N lines
    lines = army_list_text.strip().split("\n")[:max_lines]
    text_to_search = "\n".join(lines).lower()

    # First, try to match exact faction names (highest priority)
    for faction in ARMY_FACTIONS:
        if faction.lower() in text_to_search:
            return faction

    # Then try keyword patterns
    for pattern, faction in ARMY_DETECTION_PATTERNS.items():
        if pattern in text_to_search:
            return faction

    return None

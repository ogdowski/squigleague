# herald/words.py
import random
import secrets
from typing import Optional

# 50 ADJECTIVES - Colors, traits, war terms
ADJECTIVES = [
    # Colors (15)
    "crimson",
    "purple",
    "darken",
    "silver",
    "emerald",
    "azure",
    "obsidian",
    "jade",
    "scarlet",
    "cobalt",
    "bronze",
    "amber",
    "ivory",
    "onyx",
    "ruby",
    # Positive traits (15)
    "ancient",
    "blessed",
    "eternal",
    "holy",
    "mighty",
    "noble",
    "radiant",
    "sacred",
    "valiant",
    "glorious",
    "imperial",
    "legendary",
    "supreme",
    "divine",
    "exalted",
    # Negative/chaos traits (10)
    "cursed",
    "doomed",
    "fallen",
    "twisted",
    "corrupted",
    "warp",
    "chaos",
    "bed",
    "plagued",
    "tainted",
    # Neutral/war traits (10)
    "furious",
    "grim",
    "iron",
    "raging",
    "savage",
    "storm",
    "thunder",
    "vengeful",
    "void",
    "zealous",
]

# 50 WARHAMMER NOUNS - Units, races, characters
NOUNS_WARHAMMER = [
    # Orks (5)
    "ork",
    "grot",
    "nob",
    "warboss",
    "weirdboy",
    # Space Marines (10)
    "marine",
    "captain",
    "chaplain",
    "dreadnought",
    "terminator",
    "scout",
    "apothecary",
    "techmarine",
    "librarian",
    "sergeant",
    # Eldar (6)
    "eldar",
    "farseer",
    "banshee",
    "guardian",
    "wraithknight",
    "autarch",
    # Tau (5)
    "tau",
    "crisis",
    "riptide",
    "kroot",
    "ethereal",
    # Necrons (6)
    "necron",
    "lord",
    "warrior",
    "wraith",
    "scarab",
    "immortal",
    # Tyranids (6)
    "tyranid",
    "carnifex",
    "hive",
    "genestealer",
    "termagant",
    "lictor",
    # Chaos (6)
    "daemon",
    "bloodletter",
    "plaguebearer",
    "herald",
    "cultist",
    "sorcerer",
    # Imperial Guard/Knights (6)
    "knight",
    "titan",
    "sentinel",
    "chimera",
    "basilisk",
    "valkyrie",
]

# 50 VERBS - Battle actions
VERBS = [
    # Combat actions (20)
    "charges",
    "strikes",
    "shoots",
    "smites",
    "purges",
    "slays",
    "crushes",
    "destroys",
    "annihilates",
    "decimates",
    "assaults",
    "attacks",
    "raids",
    "invades",
    "sieges",
    "storms",
    "conquers",
    "vanquishes",
    "battles",
    "fights",
    # Mobility actions (10)
    "flies",
    "teleports",
    "advances",
    "marches",
    "rushes",
    "leaps",
    "dashes",
    "surges",
    "sweeps",
    "descends",
    # Special/power actions (10)
    "awakens",
    "rises",
    "emerges",
    "manifests",
    "summons",
    "channels",
    "casts",
    "conjures",
    "invokes",
    "unleashes",
    # Characteristic actions (10)
    "waaagh",
    "roars",
    "howls",
    "screams",
    "bellows",
    "commands",
    "leads",
    "guards",
    "defends",
    "endures",
]


def generate_exchange_id(check_exists_callback: Optional[callable] = None) -> str:
    """
    Generate unique exchange ID in format: adjective-noun-verb-XXXX

    Args:
        check_exists_callback: Optional function to check if ID already exists

    Returns:
        str: Unique exchange ID

    Total combinations: 50 × 50 × 50 × 65,536 = 8,192,000,000
    """
    max_attempts = 10

    for _ in range(max_attempts):
        adj = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS_WARHAMMER)
        verb = random.choice(VERBS)
        mini_hash = secrets.token_hex(2)  # 4 hex characters (0000-ffff)

        exchange_id = f"{adj}-{noun}-{verb}-{mini_hash}"

        # Check if ID already exists in database
        if check_exists_callback:
            if not check_exists_callback(exchange_id):
                return exchange_id
        else:
            return exchange_id

    # Fallback: use longer hash (extremely rare)
    return f"{adj}-{noun}-{verb}-{secrets.token_hex(3)}"


def validate_exchange_id(exchange_id: str) -> bool:
    """
    Validate exchange ID format

    Args:
        exchange_id: ID to validate

    Returns:
        bool: True if valid format
    """
    parts = exchange_id.split("-")

    if len(parts) != 4:
        return False

    adj, noun, verb, mini_hash = parts

    # Check if words are from our dictionaries
    if adj not in ADJECTIVES:
        return False
    if noun not in NOUNS_WARHAMMER:
        return False
    if verb not in VERBS:
        return False

    # Check if mini_hash is exactly 4 hex characters
    if len(mini_hash) != 4:
        return False

    try:
        int(mini_hash, 16)  # Verify it's valid hex
    except ValueError:
        return False

    return True


# Example generated IDs:
# crimson-captain-charges-7a2f
# void-necron-awakens-b3e1
# blessed-marine-purges-4d2c
# ancient-farseer-teleports-9c4d

"""Word lists for generating memorable matchup IDs."""

import random
import string

# Age of Sigmar themed adjectives
ADJECTIVES = [
    "mighty",
    "ancient",
    "blessed",
    "cursed",
    "glorious",
    "sacred",
    "eternal",
    "forbidden",
    "mystic",
    "divine",
    "wicked",
    "radiant",
    "shadowy",
    "iron",
    "golden",
    "silver",
    "crimson",
    "azure",
    "emerald",
    "obsidian",
    "savage",
    "noble",
    "vengeful",
    "triumphant",
    "doomed",
    "hallowed",
    "profane",
    "epic",
    "legendary",
    "fearsome",
    "stalwart",
    "relentless",
    "valiant",
    "zealous",
    "grim",
    "feral",
    "primal",
    "corrupted",
    "purified",
    "exalted",
]

# Age of Sigmar themed nouns (creatures, units, concepts)
NOUNS = [
    "orruk",
    "stormcast",
    "skaven",
    "seraphon",
    "nighthaunt",
    "dragon",
    "daemon",
    "warrior",
    "mage",
    "beast",
    "knight",
    "slayer",
    "champion",
    "warlord",
    "prophet",
    "shaman",
    "priest",
    "lord",
    "king",
    "queen",
    "titan",
    "guardian",
    "hunter",
    "reaper",
    "crusader",
    "templar",
    "vanguard",
    "sentinel",
    "berserker",
    "warlock",
    "sorcerer",
    "necromancer",
    "vampire",
    "ghoul",
    "zombie",
    "skeleton",
    "phoenix",
    "griffin",
    "manticore",
    "chimera",
    "hydra",
    "kraken",
    "leviathan",
]


def generate_code() -> str:
    """Generate a random 4-character alphanumeric code."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=4))


def generate_matchup_id() -> str:
    """Generate a memorable matchup ID like 'mighty-dragon-a7b2'."""
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    code = generate_code()
    return f"{adjective}-{noun}-{code}"

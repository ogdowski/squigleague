import random
from datetime import datetime

from app.matchup.models import Matchup
from sqlmodel import Session

# Hardcoded maps from GHB 2025/2026 (will be replaced with BSData later)
MAPS = [
    "Passing Seasons",
    "Paths of the Fey",
    "Roiling Roots",
    "Cyclic Shifts",
    "Surge of Slaughter",
    "Linked Ley Lines",
    "Noxious Nexus",
    "The Liferoots",
    "Bountiful Equinox",
    "Lifecycle",
    "Creeping Corruption",
    "Grasp of Thorns",
]

# Map names to battle plan image filenames
MAP_IMAGES = {
    "Passing Seasons": "aos-passing-seasons-matplotlib.png",
    "Paths of the Fey": "aos-paths-of-the-fey-matplotlib.png",
    "Roiling Roots": "aos-roiling-roots-matplotlib.png",
    "Cyclic Shifts": "aos-cyclic-shifts-matplotlib.png",
    "Surge of Slaughter": "aos-surge-of-slaughter-matplotlib.png",
    "Linked Ley Lines": "aos-linked-ley-lines-matplotlib.png",
    "Noxious Nexus": "aos-noxious-nexus-matplotlib.png",
    "The Liferoots": "aos-the-liferoots-matplotlib.png",
    "Bountiful Equinox": "aos-bountiful-equinox-matplotlib.png",
    "Lifecycle": "aos-lifecycle-matplotlib.png",
    "Creeping Corruption": "aos-creeping-corruption-matplotlib.png",
    "Grasp of Thorns": "aos-grasp-of-thorns-matplotlib.png",
}

# Battle plan detailed information from GHB 2025-2026
BATTLE_PLAN_DATA = {
    "Passing Seasons": {
        "deployment": "Long edge deployment",
        "objectives": "Gnarlroot and Oakenbrow objectives at 24\" and 48\" from long edges",
        "scoring": "Battle rounds 1,3,5: 5 VP per Gnarlroot objective. Battle rounds 2,4: 5 VP per Oakenbrow objective.",
        "underdog_ability": "Burgeoning Rejuvenation: Heal D3 on Oakenbrow objectives OR add ward save to Gnarlroot objectives",
        "objective_types": ["Gnarlroot", "Oakenbrow"],
    },
    "Paths of the Fey": {
        "deployment": "Long edge deployment",
        "objectives": "Central Heartwood, Gnarlroot at 12\" from center, Oakenbrow at 12\" from center, Winterleaf at 24\" from center",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2 or more objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "The Spirit Paths Open: Pick 2 objectives - remove nearby units and set them up within 3\" of those objectives",
        "objective_types": ["Heartwood", "Gnarlroot", "Oakenbrow", "Winterleaf"],
    },
    "Roiling Roots": {
        "deployment": "Diagonal corner deployment",
        "objectives": "6 objectives in diagonal line across battlefield",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control any pairs of objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Tangling Tendrils: Pick a pair of objectives - units contesting them have STRIKE-LAST",
        "objective_types": [],
    },
    "Cyclic Shifts": {
        "deployment": "Diagonal corner deployment",
        "objectives": "6 objectives in diagonal rows, 3 per player's side",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2 or more objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Unpredictable Evolution: Pick a pair of objectives - they cannot be controlled this battle round",
        "objective_types": [],
    },
    "Surge of Slaughter": {
        "deployment": "Long edge deployment",
        "objectives": "Central Heartwood objective and 4 corner objectives",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control any pairs of objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Defence of the Realm: Pick a pair of objectives - add 1 to Rend for units contesting them",
        "objective_types": ["Heartwood"],
    },
    "Linked Ley Lines": {
        "deployment": "Long edge deployment",
        "objectives": "5 objectives in diamond formation with linked ley lines",
        "scoring": "3 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control any pairs. 2 VP if you control all objectives on a linked ley line.",
        "underdog_ability": "Rooted in the Realm: Anti-MANIFESTATION(+1 Rend) on linked ley lines. MANIFESTATIONS have STRIKE-FIRST",
        "objective_types": [],
    },
    "Noxious Nexus": {
        "deployment": "Quadrant deployment",
        "objectives": "3 Nexus Points: Oakenbrow, Gnarlroot, and Heartwood",
        "scoring": "Cannot control in round 1. 5 VP for Oakenbrow, 3 VP for Gnarlroot, 2 VP for Heartwood. Bonus 10 VP at end of battle if you control Heartwood.",
        "underdog_ability": "Caustic Sap: Pick an objective - roll D3 for each unit contesting it, on 2+ inflict that many mortal wounds (D6 for Heartwood)",
        "objective_types": ["Oakenbrow", "Gnarlroot", "Heartwood"],
    },
    "The Liferoots": {
        "deployment": "Diagonal corner deployment",
        "objectives": "2 Liferoot markers on diagonal, 24\" apart. Terrain features provide liferoot points.",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control both objectives. 2 VP if you have more liferoot points (1 per terrain feature controlled).",
        "underdog_ability": "Life Begets Life: Return 1 slain model to a unit within 1\" of terrain",
        "objective_types": ["Liferoot"],
    },
    "Bountiful Equinox": {
        "deployment": "Long edge deployment",
        "objectives": "5 objectives spread across battlefield: Oakenbrow, Gnarlroot, and Heartwood types",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control at least 1 Oakenbrow, 1 Gnarlroot, and 1 Heartwood.",
        "underdog_ability": "Rejuvenating Bloom: Pick an objective - Heal(3) each unit contesting it",
        "objective_types": ["Oakenbrow", "Gnarlroot", "Heartwood"],
    },
    "Lifecycle": {
        "deployment": "Long edge deployment",
        "objectives": "4 lifecycle objectives in symmetrical placement with rotating primary/secondary status",
        "scoring": "4 VP if you control at least 1 objective. 2 VP if you control more objectives. Round 1: 4 VP for both Oakenbrow and Gnarlroot. After: 2 VP for primary, 1 VP per secondary.",
        "underdog_ability": "Lifecycle: Pick which objective starts as primary. Rotates each round. Primary worth 2 VP, adjacent secondaries worth 1 VP each",
        "objective_types": ["Oakenbrow", "Gnarlroot"],
    },
    "Creeping Corruption": {
        "deployment": "Long edge deployment",
        "objectives": "6 objective grid evenly spaced across battlefield",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Pulsing Life Energies: Draw line between 2 objectives - Propagation (+1 to casts/chants) OR Corruption (D3 mortal wounds to units crossed)",
        "objective_types": [],
    },
    "Grasp of Thorns": {
        "deployment": "Quadrant deployment",
        "objectives": "4 thorn objectives, one in each table quarter",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Carnivorous Flora: Pick an objective - roll for each contesting unit, on 3+ models in control zone are entangled (can't move out or be removed)",
        "objective_types": [],
    },
}


def get_map_image(map_name: str) -> str | None:
    """Get battle plan image filename for a map name."""
    return MAP_IMAGES.get(map_name)


def get_battle_plan_data(map_name: str) -> dict | None:
    """Get full battle plan data for a map name."""
    return BATTLE_PLAN_DATA.get(map_name)


def draw_random_map() -> str:
    """Draw a random map from the available maps."""
    return random.choice(MAPS)


def reveal_matchup(matchup: Matchup, session: Session) -> Matchup:
    """Reveal matchup by assigning a random map."""
    if not matchup.is_revealed:
        raise ValueError("Both players must submit their lists before revealing")

    if matchup.map_name:
        return matchup  # Already revealed

    matchup.map_name = draw_random_map()
    matchup.revealed_at = datetime.utcnow()

    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    return matchup


def submit_list(
    matchup: Matchup,
    army_list: str,
    is_player1: bool,
    session: Session,
    user_id: int = None,
) -> Matchup:
    """Submit an army list for a matchup."""
    if is_player1:
        if matchup.player1_submitted:
            raise ValueError("Player 1 has already submitted their list")
        matchup.player1_list = army_list
        matchup.player1_submitted = True
        if user_id and not matchup.player1_id:
            matchup.player1_id = user_id
    else:
        if matchup.player2_submitted:
            raise ValueError("Player 2 has already submitted their list")
        matchup.player2_list = army_list
        matchup.player2_submitted = True
        if user_id:
            matchup.player2_id = user_id

    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    # Auto-reveal if both lists are submitted
    if matchup.is_revealed and not matchup.map_name:
        matchup = reveal_matchup(matchup, session)

    return matchup

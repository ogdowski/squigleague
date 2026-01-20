"""Constants for the league module."""

# GHB 2025/2026 missions
MISSION_MAPS = [
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
        "objectives": 'Gnarlroot and Oakenbrow objectives at 24" and 48" from long edges',
        "scoring": "Battle rounds 1,3,5: 5 VP per Gnarlroot objective. Battle rounds 2,4: 5 VP per Oakenbrow objective.",
        "underdog_ability": "Burgeoning Rejuvenation: Heal D3 on Oakenbrow objectives OR add ward save to Gnarlroot objectives",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Paths of the Fey": {
        "deployment": "Long edge deployment",
        "objectives": 'Central Heartwood, Gnarlroot at 12" from center, Oakenbrow at 12" from center, Winterleaf at 24" from center',
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2 or more objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": 'The Spirit Paths Open: Pick 2 objectives - remove nearby units and set them up within 3" of those objectives',
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Roiling Roots": {
        "deployment": "Diagonal corner deployment",
        "objectives": "6 objectives in diagonal line across battlefield",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control any pairs of objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Tangling Tendrils: Pick a pair of objectives - units contesting them have STRIKE-LAST",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Cyclic Shifts": {
        "deployment": "Diagonal corner deployment",
        "objectives": "6 objectives in diagonal rows, 3 per player's side",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2 or more objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Unpredictable Evolution: Pick a pair of objectives - they cannot be controlled this battle round",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Surge of Slaughter": {
        "deployment": "Long edge deployment",
        "objectives": "Central Heartwood objective and 4 corner objectives",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control any pairs of objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Defence of the Realm: Pick a pair of objectives - add 1 to Rend for units contesting them",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Linked Ley Lines": {
        "deployment": "Long edge deployment",
        "objectives": "5 objectives in diamond formation with linked ley lines",
        "scoring": "3 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control any pairs. 2 VP if you control all objectives on a linked ley line.",
        "underdog_ability": "Rooted in the Realm: Anti-MANIFESTATION(+1 Rend) on linked ley lines. MANIFESTATIONS have STRIKE-FIRST",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Noxious Nexus": {
        "deployment": "Quadrant deployment",
        "objectives": "3 Nexus Points: Oakenbrow, Gnarlroot, and Heartwood",
        "scoring": "Cannot control in round 1. 5 VP for Oakenbrow, 3 VP for Gnarlroot, 2 VP for Heartwood. Bonus 10 VP at end of battle if you control Heartwood.",
        "underdog_ability": "Caustic Sap: Pick an objective - roll D3 for each unit contesting it, on 2+ inflict that many mortal wounds (D6 for Heartwood)",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "The Liferoots": {
        "deployment": "Diagonal corner deployment",
        "objectives": '2 Liferoot markers on diagonal, 24" apart. Terrain features provide liferoot points.',
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control both objectives. 2 VP if you have more liferoot points (1 per terrain feature controlled).",
        "underdog_ability": 'Life Begets Life: Return 1 slain model to a unit within 1" of terrain',
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Bountiful Equinox": {
        "deployment": "Long edge deployment",
        "objectives": "5 objectives spread across battlefield: Oakenbrow, Gnarlroot, and Heartwood types",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control at least 1 Oakenbrow, 1 Gnarlroot, and 1 Heartwood.",
        "underdog_ability": "Rejuvenating Bloom: Pick an objective - Heal(3) each unit contesting it",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Lifecycle": {
        "deployment": "Long edge deployment",
        "objectives": "4 lifecycle objectives in symmetrical placement with rotating primary/secondary status",
        "scoring": "4 VP if you control at least 1 objective. 2 VP if you control more objectives. Round 1: 4 VP for both Oakenbrow and Gnarlroot. After: 2 VP for primary, 1 VP per secondary.",
        "underdog_ability": "Lifecycle: Pick which objective starts as primary. Rotates each round. Primary worth 2 VP, adjacent secondaries worth 1 VP each",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Creeping Corruption": {
        "deployment": "Long edge deployment",
        "objectives": "6 objective grid evenly spaced across battlefield",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Pulsing Life Energies: Draw line between 2 objectives - Propagation (+1 to casts/chants) OR Corruption (D3 mortal wounds to units crossed)",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
    "Grasp of Thorns": {
        "deployment": "Quadrant deployment",
        "objectives": "4 thorn objectives, one in each table quarter",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Carnivorous Flora: Pick an objective - roll for each contesting unit, on 3+ models in control zone are entangled (can't move out or be removed)",
        "objective_types": ["Gnarlroot", "Oakenbrow", "Heartwood", "Winterleaf"],
    },
}

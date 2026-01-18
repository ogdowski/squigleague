"""
Extract battlefield object positions for Age of Sigmar missions.
Based on General's Handbook 2025-2026 mission specifications.
Battlefield size: 60" x 44"
"""

MISSIONS = {
    "aos-passing-seasons": {
        "name": "Passing Seasons",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 22), (30, 22), (30, 44), (0, 44)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(30, 0), (60, 0), (60, 22), (30, 22)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
            {"name": "Red NW", "x": 15, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "Green NE", "x": 45, "y": 33, "color": "green", "type": "objective", "size": "large"},
            {"name": "Green SW", "x": 15, "y": 11, "color": "green", "type": "objective", "size": "large"},
            {"name": "Red SE", "x": 45, "y": 11, "color": "red", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power W", "x": 15, "y": 22, "type": "place_of_power", "size": "large"},
            {"name": "Place of Power E", "x": 45, "y": 22, "type": "place_of_power", "size": "large"},
            {"name": "Place of Power NE", "x": 52.5, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power SW", "x": 7.5, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Ruins N", "x": 30, "y": 33, "type": "ruins"},
            {"name": "Ruins S", "x": 30, "y": 11, "type": "ruins"},
            {"name": "Forest NW", "x": 7.5, "y": 38.5, "type": "forest"},
            {"name": "Forest SE", "x": 52.5, "y": 5.5, "type": "forest"},
        ]
    },
    "aos-bountiful-equinox": {
        "name": "Bountiful Equinox",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 22), (0, 22)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 22), (60, 22), (60, 44), (0, 44)]},
        ],
        "exclusion_zones": [
            {"player": "Attacker", "color": "#666666", "alpha": 0.15, "coords": [(0, 13), (60, 13), (60, 22), (0, 22)], "note": "9\" from middle"},
            {"player": "Defender", "color": "#666666", "alpha": 0.15, "coords": [(0, 22), (60, 22), (60, 31), (0, 31)], "note": "9\" from middle"},
        ],
        "objectives": [
            {"name": "Center", "x": 30.0, "y": 22.0, "color": "blue", "type": "objective", "size": "large"},
            {"name": "Upper-Right", "x": 45, "y": 33, "color": "green", "type": "objective", "size": "large"},
            {"name": "Lower-Left", "x": 15, "y": 11, "color": "green", "type": "objective", "size": "large"},
            {"name": "Upper-Left", "x": 15, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "Lower-Right", "x": 45, "y": 11, "color": "red", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power L-Upper", "x": 9.9, "y": 27.7, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power R-Upper", "x": 53.7, "y": 27.7, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power L-Lower", "x": 6.0, "y": 17.0, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power R-Lower", "x": 49.8, "y": 17.0, "type": "place_of_power", "size": "small"},
            {"name": "Forest N", "x": 30, "y": 30.5, "type": "forest", "size": "large"},
            {"name": "Forest W", "x": 20, "y": 22, "type": "forest", "size": "large"},
            {"name": "Forest E", "x": 40, "y": 22, "type": "forest", "size": "large"},
            {"name": "Forest S", "x": 30, "y": 13.5, "type": "forest", "size": "large"},
        ]
    },
    "aos-creeping-corruption": {
        "name": "Creeping Corruption",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 22), (0, 22)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 22), (60, 22), (60, 44), (0, 44)]},
        ],
        "exclusion_zones": [
            {"player": "Attacker", "color": "#666666", "alpha": 0.15, "coords": [(0, 13), (60, 13), (60, 22), (0, 22)], "note": "9\" from middle"},
            {"player": "Defender", "color": "#666666", "alpha": 0.15, "coords": [(0, 22), (60, 22), (60, 31), (0, 31)], "note": "9\" from middle"},
        ],
        "objectives": [
            {"name": "Blue Center-Top", "x": 30, "y": 33, "color": "blue", "type": "objective", "size": "large"},
            {"name": "Red A Upper-Left", "x": 7.5, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "Red B Lower-Right", "x": 52.5, "y": 11, "color": "red", "type": "objective", "size": "large"},
            {"name": "Green A Upper-Right", "x": 52.5, "y": 33, "color": "green", "type": "objective", "size": "large"},
            {"name": "Green B Lower-Left", "x": 7.5, "y": 11, "color": "green", "type": "objective", "size": "large"},
            {"name": "Violet Bottom-Center", "x": 30, "y": 11, "color": "purple", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power Left", "x": 5, "y": 22, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power Right", "x": 55, "y": 22, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power Lower-Right", "x": 40, "y": 10, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power Upper-Left", "x": 20, "y": 34, "type": "place_of_power", "size": "small"},
            {"name": "Forest Lower-Right", "x": 42, "y": 20, "type": "forest", "size": "large"},
            {"name": "Forest Upper-Left", "x": 18, "y": 24, "type": "forest", "size": "large"},
            {"name": "Ruins Lower-Left", "x": 18, "y": 9.5, "type": "ruins", "size": "large"},
            {"name": "Ruins Upper-Right", "x": 42, "y": 34.5, "type": "ruins", "size": "large"},
        ]
    },
    "aos-cyclic-shifts": {
        "name": "Cyclic Shifts",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 11), (0, 11)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 33), (60, 33), (60, 44), (0, 44)]},
        ],
        "exclusion_zones": [
            # No exclusion zones - deployment zones are >9" apart (22" neutral territory)
        ],
        "objectives": [
            {"name": "Green South", "x": 30, "y": 11, "color": "green", "type": "objective", "size": "large"},
            {"name": "Green North", "x": 30, "y": 33, "color": "green", "type": "objective", "size": "large"},
            {"name": "Red Southwest", "x": 7.5, "y": 17.5, "color": "red", "type": "objective", "size": "large"},
            {"name": "Red Northeast", "x": 52.5, "y": 26.5, "color": "red", "type": "objective", "size": "large"},
            {"name": "Blue Grid-1", "x": 7.5, "y": 38.5, "color": "blue", "type": "objective", "size": "large"},
            {"name": "Purple Grid-16", "x": 52.5, "y": 5.5, "color": "purple", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Forest G3", "x": 41.25, "y": 34.75, "type": "forest", "size": "large"},
            {"name": "Forest G14", "x": 18.75, "y": 8.25, "type": "forest", "size": "large"},
            {"name": "Ruins G2", "x": 18.75, "y": 35.75, "type": "ruins", "size": "small"},
            {"name": "Ruins G15", "x": 41.25, "y": 8.25, "type": "ruins", "size": "small"},
            {"name": "Place of Power G5", "x": 9, "y": 27.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power G12", "x": 51, "y": 16.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power G6", "x": 24, "y": 23.5, "type": "place_of_power", "size": "large"},
            {"name": "Place of Power G11", "x": 36, "y": 20.5, "type": "place_of_power", "size": "large"},
        ]
    },
    "aos-grasp-of-thorns": {
        "name": "Grasp of Thorns",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 22), (60, 22), (60, 44), (0, 44)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 22), (0, 22)]},
        ],
        "exclusion_zones": [
            {"color": "#666666", "alpha": 0.15, "coords": [(0, 13), (60, 13), (60, 22), (0, 22)], "note": "9\" from middle line (lower)"},
            {"color": "#666666", "alpha": 0.15, "coords": [(0, 22), (60, 22), (60, 31), (0, 31)], "note": "9\" from middle line (upper)"},
        ],
        "objectives": [
            {"name": "Green Top-Left", "x": 15, "y": 33, "color": "green", "type": "objective", "size": "large"},
            {"name": "Purple Top-Right", "x": 45, "y": 33, "color": "purple", "type": "objective", "size": "large"},
            {"name": "Blue Bottom-Left", "x": 15, "y": 11, "color": "blue", "type": "objective", "size": "large"},
            {"name": "Red Bottom-Right", "x": 45, "y": 11, "color": "red", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Forest G5", "x": 7.5, "y": 27.5, "type": "forest", "size": "large"},
            {"name": "Forest G12", "x": 52.5, "y": 16.5, "type": "forest", "size": "large"},
            {"name": "Place of Power G2", "x": 20, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power G15", "x": 40, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power G3", "x": 33, "y": 35.5, "type": "place_of_power", "size": "large"},
            {"name": "Place of Power G14", "x": 27, "y": 8.5, "type": "place_of_power", "size": "large"},
            {"name": "Ruins G6", "x": 22.5, "y": 24, "type": "ruins", "size": "large"},
            {"name": "Ruins G11", "x": 37.5, "y": 20, "type": "ruins", "size": "large"},
        ]
    },
    "aos-lifecycle": {
        "name": "Lifecycle",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 33), (60, 33), (60, 44), (0, 44)]},
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 22), (15, 22), (15, 33), (0, 33)]},
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(45, 22), (60, 22), (60, 33), (45, 33)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 11), (0, 11)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 11), (15, 11), (15, 22), (0, 22)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(45, 11), (60, 11), (60, 22), (45, 22)]},
            {"player": "Neutral", "color": "#cccccc", "alpha": 0.2, "coords": [(15, 11), (45, 11), (45, 33), (15, 33)]},
        ],
        "exclusion_zones": [
        ],
        "objectives": [
            {"name": "Purple North", "x": 30, "y": 33, "color": "purple", "type": "objective", "size": "large"},
            {"name": "Green East", "x": 45, "y": 22, "color": "green", "type": "objective", "size": "large"},
            {"name": "Blue South", "x": 30, "y": 11, "color": "blue", "type": "objective", "size": "large"},
            {"name": "Red West", "x": 15, "y": 22, "color": "red", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Forest G4", "x": 46.75, "y": 34.75, "type": "forest", "size": "large"},
            {"name": "Forest G13", "x": 13.25, "y": 9.25, "type": "forest", "size": "large"},
            {"name": "Place of Power 1", "x": 22.5, "y": 22, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power 2", "x": 37.5, "y": 22, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power 3", "x": 7.5, "y": 28, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power 4", "x": 52.5, "y": 16, "type": "place_of_power", "size": "small"},
            {"name": "Ruins North", "x": 18.5, "y": 33, "type": "ruins", "size": "large"},
            {"name": "Ruins South", "x": 41.5, "y": 11, "type": "ruins", "size": "large"},
        ]
    },
    "aos-linked-ley-lines": {
        "name": "Linked Ley Lines",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 11), (0, 11)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 33), (60, 33), (60, 44), (0, 44)]},
        ],
        "exclusion_zones": [
            # No exclusion zones - deployment zones are >9" apart (22" neutral territory)
        ],
        "objectives": [
            {"name": "Blue Center", "x": 30, "y": 22, "color": "blue", "type": "objective", "size": "large"},
            {"name": "Red South", "x": 30, "y": 11, "color": "red", "type": "objective", "size": "large"},
            {"name": "Red North", "x": 30, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "Green West", "x": 15, "y": 22, "color": "green", "type": "objective", "size": "large"},
            {"name": "Green East", "x": 45, "y": 22, "color": "green", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Forest Northeast", "x": 41.5, "y": 33, "type": "forest", "size": "large"},
            {"name": "Forest Southwest", "x": 18.5, "y": 11, "type": "forest", "size": "large"},
            {"name": "Place of Power Northwest", "x": 18, "y": 34.5, "type": "place_of_power", "size": "large"},
            {"name": "Place of Power Southeast", "x": 42, "y": 9.5, "type": "place_of_power", "size": "large"},
            {"name": "Place of Power West", "x": 5, "y": 22, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power East", "x": 55, "y": 22, "type": "place_of_power", "size": "small"},
            {"name": "Ruins Northwest", "x": 6, "y": 36, "type": "ruins", "size": "large"},
            {"name": "Ruins Southeast", "x": 54, "y": 8, "type": "ruins", "size": "large"},
        ]
    },
    "aos-noxious-nexus": {
        "name": "Noxious Nexus",
        "deployment_zones": [
            {"player": "Neutral", "color": "#666666", "alpha": 0.2, "coords": [(0, 0), (30, 0), (30, 44), (0, 44)]},
            {"player": "Red", "color": "#dc3545", "alpha": 0.3, "coords": [(30, 22), (60, 22), (60, 44), (30, 44)]},
            {"player": "Blue", "color": "#007bff", "alpha": 0.3, "coords": [(30, 0), (60, 0), (60, 22), (30, 22)]},
        ],
        "exclusion_zones": [
            {"type": "rect", "coords": [(30, 13), (60, 13), (60, 22), (30, 22)], "color": "#666666", "alpha": 0.15, "note": "9\" from blue edge"},
            {"type": "rect", "coords": [(30, 22), (60, 22), (60, 31), (30, 31)], "color": "#666666", "alpha": 0.15, "note": "9\" from red edge"},
        ],
        "objectives": [
            {"name": "West", "x": 15, "y": 22, "color": "blue", "type": "objective", "size": "large"},
            {"name": "Center", "x": 30, "y": 22, "color": "green", "type": "objective", "size": "large"},
            {"name": "East", "x": 45, "y": 22, "color": "red", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Ruins W", "x": 5, "y": 22, "type": "ruins", "size": "small"},
            {"name": "Ruins E", "x": 55, "y": 22, "type": "ruins", "size": "small"},
            {"name": "Forest N1", "x": 22.5, "y": 33, "type": "forest", "size": "large"},
            {"name": "Forest S1", "x": 22.5, "y": 11, "type": "forest", "size": "large"},
            {"name": "Forest N2", "x": 46, "y": 35, "type": "forest", "size": "large"},
            {"name": "Forest S2", "x": 46, "y": 9, "type": "forest", "size": "large"},
            {"name": "PoP N", "x": 37.5, "y": 27.5, "type": "place_of_power", "size": "small"},
            {"name": "PoP S", "x": 37.5, "y": 16.5, "type": "place_of_power", "size": "small"},
        ]
    },
    "aos-paths-of-the-fey": {
        "name": "Paths of the Fey",
        "deployment_zones": [
            {"player": "Neutral L", "color": "#666666", "alpha": 0.2, "coords": [(0, 0), (15, 0), (15, 44), (0, 44)]},
            {"player": "Neutral R", "color": "#666666", "alpha": 0.2, "coords": [(45, 0), (60, 0), (60, 44), (45, 44)]},
            {"player": "Red", "color": "#dc3545", "alpha": 0.3, "coords": [(15, 22), (45, 22), (45, 44), (15, 44)]},
            {"player": "Blue", "color": "#007bff", "alpha": 0.3, "coords": [(15, 0), (45, 0), (45, 22), (15, 22)]},
        ],
        "exclusion_zones": [
            {"type": "rect", "coords": [(15, 13), (45, 13), (45, 22), (15, 22)], "color": "#666666", "alpha": 0.15, "note": "9\" from blue edge"},
            {"type": "rect", "coords": [(15, 22), (45, 22), (45, 31), (15, 31)], "color": "#666666", "alpha": 0.15, "note": "9\" from red edge"},
        ],
        "objectives": [
            {"name": "Blue Center", "x": 30, "y": 22, "color": "blue", "type": "objective", "size": "large"},
            {"name": "Red NW", "x": 7.5, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "Red SE", "x": 52.5, "y": 11, "color": "red", "type": "objective", "size": "large"},
            {"name": "Green SW", "x": 7.5, "y": 11, "color": "green", "type": "objective", "size": "large"},
            {"name": "Green NE", "x": 52.5, "y": 33, "color": "green", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Forest NW", "x": 19, "y": 31, "type": "forest", "size": "large"},
            {"name": "Forest SE", "x": 41, "y": 13, "type": "forest", "size": "large"},
            {"name": "Forest NE", "x": 37.5, "y": 35, "type": "forest", "size": "large"},
            {"name": "Forest SW", "x": 22.5, "y": 9, "type": "forest", "size": "large"},
            {"name": "Ruins W", "x": 20, "y": 22, "type": "ruins", "size": "small"},
            {"name": "Ruins E", "x": 40, "y": 22, "type": "ruins", "size": "small"},
            {"name": "PoP SW", "x": 7.5, "y": 21, "type": "place_of_power", "size": "small"},
            {"name": "PoP NE", "x": 52.5, "y": 23, "type": "place_of_power", "size": "small"},
        ]
    },
    "aos-roiling-roots": {
        "name": "Roiling Roots",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 19), (0, 19)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 25), (60, 25), (60, 44), (0, 44)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
            {"name": "NW", "x": 7.5, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "N-Center", "x": 30, "y": 33, "color": "green", "type": "objective", "size": "large"},
            {"name": "NE", "x": 52.5, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "SW", "x": 7.5, "y": 11, "color": "green", "type": "objective", "size": "large"},
            {"name": "S-Center", "x": 30, "y": 11, "color": "green", "type": "objective", "size": "large"},
            {"name": "SE", "x": 52.5, "y": 11, "color": "red", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power W", "x": 7.5, "y": 22, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power E", "x": 52.5, "y": 22, "type": "place_of_power", "size": "small"},
            {"name": "Ruins NW", "x": 15, "y": 38.5, "type": "ruins"},
            {"name": "Ruins S", "x": 30, "y": 5.5, "type": "ruins"},
            {"name": "Forest NE", "x": 45, "y": 38.5, "type": "forest"},
            {"name": "Forest SW", "x": 15, "y": 5.5, "type": "forest"},
        ]
    },
    "aos-surge-of-slaughter": {
        "name": "Surge of Slaughter",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 19), (0, 19)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 25), (60, 25), (60, 44), (0, 44)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
            {"name": "West", "x": 15, "y": 22, "color": "red", "type": "objective", "size": "large"},
            {"name": "Center", "x": 30, "y": 22, "color": "blue", "type": "objective", "size": "large"},
            {"name": "East", "x": 45, "y": 22, "color": "green", "type": "objective", "size": "large"},
            {"name": "North", "x": 30, "y": 33, "color": "purple", "type": "objective", "size": "large"},
            {"name": "South", "x": 30, "y": 11, "color": "red", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power NW", "x": 7.5, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power NE", "x": 52.5, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power SW", "x": 7.5, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power SE", "x": 52.5, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Ruins NW", "x": 15, "y": 33, "type": "ruins"},
            {"name": "Ruins SE", "x": 45, "y": 11, "type": "ruins"},
            {"name": "Forest NE", "x": 45, "y": 33, "type": "forest"},
            {"name": "Forest SW", "x": 15, "y": 11, "type": "forest"},
        ]
    },
    "aos-the-liferoots": {
        "name": "The Liferoots",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 19), (0, 19)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 25), (60, 25), (60, 44), (0, 44)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
            {"name": "Center", "x": 30, "y": 22, "color": "blue", "type": "objective", "size": "large"},
            {"name": "West", "x": 7.5, "y": 22, "color": "red", "type": "objective", "size": "large"},
            {"name": "East", "x": 52.5, "y": 22, "color": "green", "type": "objective", "size": "large"},
            {"name": "North", "x": 30, "y": 33, "color": "blue", "type": "objective", "size": "large"},
            {"name": "South", "x": 30, "y": 11, "color": "purple", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power NW", "x": 15, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power SE", "x": 45, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Ruins N", "x": 22.5, "y": 33, "type": "ruins"},
            {"name": "Ruins S", "x": 37.5, "y": 11, "type": "ruins"},
            {"name": "Forest NE", "x": 52.5, "y": 38.5, "type": "forest"},
            {"name": "Forest SW", "x": 7.5, "y": 5.5, "type": "forest"},
        ]
    },
}

if __name__ == "__main__":
    import json
    print(json.dumps(MISSIONS, indent=2))

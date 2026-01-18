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
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 19), (0, 19)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 25), (60, 25), (60, 44), (0, 44)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
        ],
        "terrain": [
        ]
    },
    "aos-grasp-of-thorns": {
        "name": "Grasp of Thorns",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 22), (30, 22), (30, 44), (0, 44)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(30, 0), (60, 0), (60, 22), (30, 22)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
            {"name": "NW", "x": 15, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "N-Center", "x": 30, "y": 33, "color": "blue", "type": "objective", "size": "large"},
            {"name": "NE", "x": 45, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "SW", "x": 15, "y": 11, "color": "blue", "type": "objective", "size": "large"},
            {"name": "S-Center", "x": 30, "y": 11, "color": "red", "type": "objective", "size": "large"},
            {"name": "SE", "x": 45, "y": 11, "color": "green", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power NW", "x": 7.5, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power SE", "x": 52.5, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Ruins N", "x": 22.5, "y": 27.5, "type": "ruins"},
            {"name": "Ruins S", "x": 37.5, "y": 16.5, "type": "ruins"},
            {"name": "Ruins E", "x": 52.5, "y": 22, "type": "ruins"},
            {"name": "Forest NW", "x": 7.5, "y": 38.5, "type": "forest"},
            {"name": "Forest SE", "x": 52.5, "y": 5.5, "type": "forest"},
        ]
    },
    "aos-lifecycle": {
        "name": "Lifecycle",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (21, 0), (21, 44), (0, 44)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(39, 0), (60, 0), (60, 44), (39, 44)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
            {"name": "Center", "x": 30, "y": 22, "color": "blue", "type": "objective", "size": "large"},
            {"name": "NW", "x": 15, "y": 33, "color": "green", "type": "objective", "size": "large"},
            {"name": "NE", "x": 45, "y": 33, "color": "green", "type": "objective", "size": "large"},
            {"name": "SW", "x": 15, "y": 11, "color": "red", "type": "objective", "size": "large"},
            {"name": "SE", "x": 45, "y": 11, "color": "red", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power N", "x": 30, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power S", "x": 30, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Ruins W", "x": 7.5, "y": 22, "type": "ruins"},
            {"name": "Ruins E", "x": 52.5, "y": 22, "type": "ruins"},
            {"name": "Forest NE", "x": 52.5, "y": 38.5, "type": "forest"},
            {"name": "Forest SW", "x": 7.5, "y": 5.5, "type": "forest"},
        ]
    },
    "aos-linked-ley-lines": {
        "name": "Linked Ley Lines",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 19), (45, 0), (60, 0), (60, 25), (15, 44), (0, 44)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 0), (0, 19), (15, 44), (60, 44), (60, 25), (45, 0)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
            {"name": "Center", "x": 30, "y": 22, "color": "blue", "type": "objective", "size": "large"},
            {"name": "North", "x": 30, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "South", "x": 30, "y": 11, "color": "red", "type": "objective", "size": "large"},
            {"name": "West", "x": 15, "y": 22, "color": "red", "type": "objective", "size": "large"},
            {"name": "East", "x": 45, "y": 22, "color": "green", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power N", "x": 52.5, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power S", "x": 7.5, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Ruins NW", "x": 7.5, "y": 33, "type": "ruins"},
            {"name": "Ruins SE", "x": 52.5, "y": 11, "type": "ruins"},
            {"name": "Forest NE", "x": 52.5, "y": 38.5, "type": "forest"},
            {"name": "Forest SW", "x": 7.5, "y": 5.5, "type": "forest"},
        ]
    },
    "aos-noxious-nexus": {
        "name": "Noxious Nexus",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (60, 0), (60, 19), (0, 19)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(0, 25), (60, 25), (60, 44), (0, 44)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
            {"name": "W-North", "x": 15, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "W-South", "x": 15, "y": 11, "color": "green", "type": "objective", "size": "large"},
            {"name": "Center", "x": 30, "y": 22, "color": "purple", "type": "objective", "size": "large"},
            {"name": "E-North", "x": 45, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "E-South", "x": 45, "y": 11, "color": "blue", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power NW", "x": 7.5, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power SE", "x": 52.5, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Ruins NW", "x": 22.5, "y": 33, "type": "ruins"},
            {"name": "Ruins S", "x": 37.5, "y": 5.5, "type": "ruins"},
            {"name": "Forest NE", "x": 52.5, "y": 33, "type": "forest"},
            {"name": "Forest SW", "x": 7.5, "y": 11, "type": "forest"},
        ]
    },
    "aos-paths-of-the-fey": {
        "name": "Paths of the Fey",
        "deployment_zones": [
            {"player": "Attacker", "color": "#dc3545", "alpha": 0.3, "coords": [(0, 0), (24, 0), (24, 44), (0, 44)]},
            {"player": "Defender", "color": "#007bff", "alpha": 0.3, "coords": [(36, 0), (60, 0), (60, 44), (36, 44)]},
        ],
        "exclusion_zones": [
            {"type": "circle", "center": (30, 22), "radius": 9, "color": "#666666", "alpha": 0.15, "note": "9\" from center point"},
        ],
        "objectives": [
            {"name": "Center", "x": 30, "y": 22, "color": "blue", "type": "objective", "size": "large"},
            {"name": "NW", "x": 15, "y": 33, "color": "red", "type": "objective", "size": "large"},
            {"name": "NE", "x": 45, "y": 33, "color": "green", "type": "objective", "size": "large"},
            {"name": "SW", "x": 15, "y": 11, "color": "red", "type": "objective", "size": "large"},
            {"name": "SE", "x": 45, "y": 11, "color": "red", "type": "objective", "size": "large"},
        ],
        "terrain": [
            {"name": "Place of Power N", "x": 30, "y": 38.5, "type": "place_of_power", "size": "small"},
            {"name": "Place of Power S", "x": 30, "y": 5.5, "type": "place_of_power", "size": "small"},
            {"name": "Ruins N", "x": 22.5, "y": 33, "type": "ruins"},
            {"name": "Ruins SE", "x": 45, "y": 5.5, "type": "ruins"},
            {"name": "Ruins SW", "x": 7.5, "y": 11, "type": "ruins"},
            {"name": "Ruins E", "x": 52.5, "y": 22, "type": "ruins"},
            {"name": "Forest NW", "x": 7.5, "y": 38.5, "type": "forest"},
            {"name": "Forest SE", "x": 52.5, "y": 5.5, "type": "forest"},
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

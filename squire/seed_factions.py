"""
Seed initial factions for all game systems
"""

from squire.database import get_session, Faction


AOS_FACTIONS = [
    {"name": "Stormcast Eternals", "description": "Immortal warriors of Sigmar"},
    {"name": "Skaven", "description": "Rat-men from beneath the cities"},
    {"name": "Ossiarch Bonereapers", "description": "Undead legions of Nagash"},
    {"name": "Lumineth Realm-lords", "description": "Aelven warriors of enlightenment"},
    {"name": "Idoneth Deepkin", "description": "Soul-stealing aelves from the seas"},
    {"name": "Daughters of Khaine", "description": "Murderous servants of the Shadow Queen"},
    {"name": "Maggotkin of Nurgle", "description": "Plagued followers of the Plague God"},
    {"name": "Hedonites of Slaanesh", "description": "Decadent servants of excess"},
    {"name": "Blades of Khorne", "description": "Blood-thirsty warriors of the Blood God"},
    {"name": "Disciples of Tzeentch", "description": "Sorcerous followers of change"},
    {"name": "Orruk Warclans", "description": "Green-skinned warriors who live for battle"},
    {"name": "Gloomspite Gitz", "description": "Moon-worshipping grots and squigs"},
    {"name": "Ogor Mawtribes", "description": "Massive nomadic raiders"},
    {"name": "Flesh-eater Courts", "description": "Delusional cannibalistic ghouls"},
    {"name": "Nighthaunt", "description": "Spectral undead legions"},
    {"name": "Soulblight Gravelords", "description": "Vampiric lords and their undead"},
    {"name": "Sylvaneth", "description": "Forest spirits and treelords"},
    {"name": "Seraphon", "description": "Lizardmen servants of the Old Ones"},
    {"name": "Cities of Sigmar", "description": "Diverse mortal civilizations"},
    {"name": "Beasts of Chaos", "description": "Mutated beasts of the dark gods"},
]

FORTY_K_FACTIONS = [
    {"name": "Space Marines", "description": "Humanity's finest warriors"},
    {"name": "Adeptus Custodes", "description": "The Emperor's personal guard"},
    {"name": "Imperial Guard", "description": "Countless soldiers of the Imperium"},
    {"name": "Adeptus Mechanicus", "description": "Tech-priests of Mars"},
    {"name": "Imperial Knights", "description": "Towering war machines"},
    {"name": "Adepta Sororitas", "description": "Battle Sisters of the Ecclesiarchy"},
    {"name": "Grey Knights", "description": "Daemon-hunting Space Marines"},
    {"name": "Chaos Space Marines", "description": "Traitor Legions from the Heresy"},
    {"name": "Chaos Daemons", "description": "Entities from the Warp"},
    {"name": "Chaos Knights", "description": "Corrupted war machines"},
    {"name": "Death Guard", "description": "Plague Marines of Nurgle"},
    {"name": "Thousand Sons", "description": "Sorcerous warriors of Tzeentch"},
    {"name": "World Eaters", "description": "Berserkers of Khorne"},
    {"name": "Orks", "description": "Green-skinned raiders and looters"},
    {"name": "Necrons", "description": "Ancient robotic warriors"},
    {"name": "Tyranids", "description": "Alien swarm from beyond the galaxy"},
    {"name": "Genestealer Cults", "description": "Alien-infected rebels"},
    {"name": "Aeldari", "description": "Ancient space elves"},
    {"name": "Drukhari", "description": "Dark Eldar raiders"},
    {"name": "T'au Empire", "description": "Technologically advanced aliens"},
    {"name": "Leagues of Votann", "description": "Space Dwarfs returning from the void"},
]

OLD_WORLD_FACTIONS = [
    {"name": "Empire of Man", "description": "Human kingdoms of the Old World"},
    {"name": "Bretonnia", "description": "Knightly realm of honor"},
    {"name": "Dwarfs", "description": "Master craftsmen and warriors"},
    {"name": "High Elves", "description": "Noble elven kingdoms"},
    {"name": "Dark Elves", "description": "Cruel raiders from Naggaroth"},
    {"name": "Wood Elves", "description": "Forest-dwelling elves and spirits"},
    {"name": "Lizardmen", "description": "Ancient servants of the Old Ones"},
    {"name": "Skaven", "description": "Rat-men dwelling beneath the world"},
    {"name": "Tomb Kings", "description": "Undead rulers of ancient Nehekhara"},
    {"name": "Vampire Counts", "description": "Undead legions led by vampires"},
    {"name": "Warriors of Chaos", "description": "Northern marauders corrupted by Chaos"},
    {"name": "Daemons of Chaos", "description": "Manifestations of the Dark Gods"},
    {"name": "Beastmen", "description": "Mutated beasts of the forests"},
    {"name": "Orcs & Goblins", "description": "Green-skinned raiders and scavengers"},
    {"name": "Ogre Kingdoms", "description": "Massive nomadic warriors"},
]


def seed_factions():
    """Seed initial factions for all game systems"""
    db = next(get_session())
    
    try:
        # Check if factions already exist
        existing_count = db.query(Faction).count()
        if existing_count > 0:
            print(f"Factions already seeded ({existing_count} factions found)")
            return
        
        # Seed Age of Sigmar
        for faction_data in AOS_FACTIONS:
            faction = Faction(
                name=faction_data["name"],
                game_system="AoS",
                description=faction_data["description"]
            )
            db.add(faction)
        
        # Seed Warhammer 40K
        for faction_data in FORTY_K_FACTIONS:
            faction = Faction(
                name=faction_data["name"],
                game_system="40K",
                description=faction_data["description"]
            )
            db.add(faction)
        
        # Seed The Old World
        for faction_data in OLD_WORLD_FACTIONS:
            faction = Faction(
                name=faction_data["name"],
                game_system="Old World",
                description=faction_data["description"]
            )
            db.add(faction)
        
        db.commit()
        print(f"Successfully seeded {len(AOS_FACTIONS) + len(FORTY_K_FACTIONS) + len(OLD_WORLD_FACTIONS)} factions")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding factions: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_factions()

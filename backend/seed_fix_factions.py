import random

from app.data.armies import ARMY_FACTIONS
from app.db import engine
from sqlmodel import Session, text

with Session(engine) as session:
    rows = session.exec(
        text("SELECT id FROM league_players WHERE group_id IS NOT NULL")
    ).all()

    for i, row in enumerate(rows):
        faction = random.choice(ARMY_FACTIONS)
        has_list = (i % 3) != 0

        if has_list:
            list_text = f"""Allegiance: {faction}

General: Warlord
- Command Trait: Strategic Genius
- Artefact: Amulet of Destiny

Battleline:
- 10x Battleline Unit
- 10x Battleline Unit  
- 5x Elite Warriors

Heroes:
- Wizard (General)
- Battle Standard Bearer
- Mounted Hero

Behemoth:
- Monster/War Machine

Total: 2000/2000 points"""
            safe_list = list_text.replace("'", "''")
            session.exec(
                text(
                    f"""
                UPDATE league_players 
                SET group_army_faction = '{faction}',
                    group_army_list = '{safe_list}',
                    knockout_army_faction = '{faction}',
                    knockout_army_list = '{safe_list}'
                WHERE id = {row[0]}
            """
                )
            )
        else:
            session.exec(
                text(
                    f"""
                UPDATE league_players 
                SET group_army_faction = '{faction}',
                    group_army_list = NULL,
                    knockout_army_faction = '{faction}',
                    knockout_army_list = NULL
                WHERE id = {row[0]}
            """
                )
            )

    session.commit()

    # Update match factions
    for m in session.exec(
        text(
            """
        SELECT m.id, lp1.group_army_faction, lp2.group_army_faction
        FROM matches m
        JOIN league_players lp1 ON m.player1_id = lp1.id
        JOIN league_players lp2 ON m.player2_id = lp2.id
    """
        )
    ).all():
        if m[1] and m[2]:
            session.exec(
                text(
                    f"UPDATE matches SET player1_army_faction='{m[1]}', player2_army_faction='{m[2]}' WHERE id={m[0]}"
                )
            )
    session.commit()

    print("Updated factions!")
    with_list = session.exec(
        text("SELECT COUNT(*) FROM league_players WHERE group_army_list IS NOT NULL")
    ).first()[0]
    without_list = session.exec(
        text(
            "SELECT COUNT(*) FROM league_players WHERE group_army_list IS NULL AND group_id IS NOT NULL"
        )
    ).first()[0]
    print(f"Players with lists: {with_list}, without: {without_list}")

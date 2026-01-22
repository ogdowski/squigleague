import random

from app.data.maps import MISSION_MAPS
from app.db import engine
from sqlmodel import Session, text


def calc_pts(s1, s2):
    if s1 > s2:
        base = 1000
    elif s1 < s2:
        base = 200
    else:
        base = 600
    return base + min(100, max(0, (s1 - s2) + 50))


with Session(engine) as session:
    session.exec(
        text(
            "UPDATE league_players SET games_played=0, games_won=0, games_drawn=0, games_lost=0, total_points=0"
        )
    )
    session.commit()

    matches = session.exec(
        text(
            "SELECT id, player1_id, player2_id, player1_score, player2_score FROM matches WHERE status = 'confirmed'"
        )
    ).all()
    print(f"Processing {len(matches)} matches...")

    for m_id, lp1, lp2, s1, s2 in matches:
        if s1 is None:
            s1, s2 = random.randint(55, 82), random.randint(55, 82)
        pts1, pts2 = calc_pts(s1, s2), calc_pts(s2, s1)
        map_name = random.choice(MISSION_MAPS)

        session.exec(
            text(
                f"UPDATE matches SET player1_score={s1}, player2_score={s2}, player1_league_points={pts1}, player2_league_points={pts2}, map_name='{map_name}' WHERE id={m_id}"
            )
        )
        session.exec(
            text(
                f"UPDATE league_players SET games_played=games_played+1, total_points=total_points+{pts1} WHERE id={lp1}"
            )
        )
        session.exec(
            text(
                f"UPDATE league_players SET games_played=games_played+1, total_points=total_points+{pts2} WHERE id={lp2}"
            )
        )

        if s1 > s2:
            session.exec(
                text(f"UPDATE league_players SET games_won=games_won+1 WHERE id={lp1}")
            )
            session.exec(
                text(
                    f"UPDATE league_players SET games_lost=games_lost+1 WHERE id={lp2}"
                )
            )
        elif s2 > s1:
            session.exec(
                text(
                    f"UPDATE league_players SET games_lost=games_lost+1 WHERE id={lp1}"
                )
            )
            session.exec(
                text(f"UPDATE league_players SET games_won=games_won+1 WHERE id={lp2}")
            )
        else:
            session.exec(
                text(
                    f"UPDATE league_players SET games_drawn=games_drawn+1 WHERE id={lp1}"
                )
            )
            session.exec(
                text(
                    f"UPDATE league_players SET games_drawn=games_drawn+1 WHERE id={lp2}"
                )
            )

    session.commit()
    print("Done!")

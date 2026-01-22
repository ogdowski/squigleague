from app.db import engine
from sqlmodel import Session, text


def calc_expected(my_elo, opp_elo):
    return 1 / (1 + 10 ** ((opp_elo - my_elo) / 400))


def calc_change(my_elo, opp_elo, result, k):
    return round(k * (result - calc_expected(my_elo, opp_elo)))


with Session(engine) as session:
    # Reset ELO
    session.exec(
        text("UPDATE player_elo SET elo=1000, games_played=0, k_factor_games=0")
    )
    session.commit()

    # Get user_id for each league_player
    lp_map = {}
    for row in session.exec(text("SELECT id, user_id FROM league_players")).all():
        lp_map[row[0]] = row[1]

    # Track ELO in memory
    elos = {}
    for row in session.exec(text("SELECT user_id FROM player_elo")).all():
        elos[row[0]] = {"elo": 1000, "games": 0, "k_games": 0}

    # Process matches in order
    matches = session.exec(
        text(
            """
        SELECT id, player1_id, player2_id, player1_score, player2_score
        FROM matches WHERE status = 'confirmed' ORDER BY id
    """
        )
    ).all()

    print(f"Processing {len(matches)} matches for ELO...")

    for m_id, lp1, lp2, s1, s2 in matches:
        u1, u2 = lp_map[lp1], lp_map[lp2]
        e1, e2 = elos[u1]["elo"], elos[u2]["elo"]

        k1 = 50 if elos[u1]["k_games"] < 5 else 32
        k2 = 50 if elos[u2]["k_games"] < 5 else 32

        if s1 > s2:
            r1, r2 = 1.0, 0.0
        elif s1 < s2:
            r1, r2 = 0.0, 1.0
        else:
            r1, r2 = 0.5, 0.5

        c1 = calc_change(e1, e2, r1, k1)
        c2 = calc_change(e2, e1, r2, k2)

        elos[u1]["elo"] += c1
        elos[u2]["elo"] += c2
        elos[u1]["games"] += 1
        elos[u2]["games"] += 1
        elos[u1]["k_games"] += 1
        elos[u2]["k_games"] += 1

        # Update match with ELO
        session.exec(
            text(
                f"""
            UPDATE matches SET 
                player1_elo_before={e1}, player1_elo_after={e1+c1},
                player2_elo_before={e2}, player2_elo_after={e2+c2}
            WHERE id={m_id}
        """
            )
        )

    # Update player_elo table
    for uid, data in elos.items():
        session.exec(
            text(
                f"UPDATE player_elo SET elo={data['elo']}, games_played={data['games']}, k_factor_games={data['k_games']} WHERE user_id={uid}"
            )
        )

    session.commit()
    print("Done!")

    # Show top ELO
    print("\nTop 10 ELO:")
    for i, row in enumerate(
        session.exec(
            text(
                "SELECT u.username, p.elo, p.games_played FROM player_elo p JOIN users u ON p.user_id=u.id ORDER BY p.elo DESC LIMIT 10"
            )
        ).all(),
        1,
    ):
        print(f"  {i:2}. {row[0]:6} {row[1]} ({row[2]} games)")

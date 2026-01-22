"""
Seed script for dev database.
Run: docker cp seed_data.py squig-backend:/app/ && docker exec squig-backend python seed_data.py
"""

import os
import sys
from datetime import datetime, timedelta
from random import choice, randint

from app.core.security import get_password_hash

# Avoid circular imports by importing from db first
from app.db import engine
from app.matchup.models import Matchup

# Import models directly, avoiding package __init__
from app.users.models import User

# These are safe as they don't trigger the circular import when imported after db
from sqlalchemy import text
from sqlmodel import Session, SQLModel, delete, select

FACTIONS = [
    "Stormcast Eternals",
    "Nighthaunt",
    "Skaven",
    "Seraphon",
    "Fyreslayers",
    "Kharadron Overlords",
    "Lumineth Realm-lords",
    "Daughters of Khaine",
    "Idoneth Deepkin",
    "Sylvaneth",
    "Cities of Sigmar",
    "Slaves to Darkness",
]

MAPS = [
    "Realmshaper Engine",
    "Focal Points",
    "The Vice",
    "Savage Gains",
    "Marking Territory",
    "Limited Resources",
    "The Prize",
    "Close to the Chest",
]


def calculate_expected_score(player_elo: int, opponent_elo: int) -> float:
    """ELO expected score calculation."""
    return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))


def calculate_elo_change(
    player_elo: int, opponent_elo: int, result: float, k_factor: int
) -> int:
    """ELO change calculation."""
    expected = calculate_expected_score(player_elo, opponent_elo)
    return round(k_factor * (result - expected))


def calculate_match_points(player_score: int, opponent_score: int) -> int:
    """League points calculation."""
    if player_score > opponent_score:
        base = 1000
    elif player_score < opponent_score:
        base = 200
    else:
        base = 600
    diff = player_score - opponent_score
    bonus = min(100, max(0, diff + 50))
    return base + bonus


def main():
    print("\n" + "=" * 60)
    print("SEEDING DEV DATABASE")
    print("=" * 60)

    with Session(engine) as session:
        # Clear tables using raw SQL to avoid import issues
        print("\nClearing existing data...")
        for table in [
            "matches",
            "league_players",
            "groups",
            "leagues",
            "matchups",
            "player_elo",
            "users",
            "app_settings",
            "army_stats",
        ]:
            try:
                session.exec(text(f"DELETE FROM {table}"))
            except Exception:
                pass
        session.commit()
        print("  Done")

        # Create settings
        print("\nCreating app settings...")
        for key, value in [
            ("elo_k_factor", "32"),
            ("elo_new_player_k", "50"),
            ("elo_new_player_games", "5"),
        ]:
            session.exec(
                text(
                    f"INSERT INTO app_settings (key, value, updated_at) VALUES ('{key}', '{value}', NOW()) ON CONFLICT (key) DO NOTHING"
                )
            )
        session.commit()

        # Create org1 (admin)
        print("\nCreating users...")
        org1 = User(
            email="org1@t.co",
            username="org1",
            hashed_password=get_password_hash("test"),
            role="admin",
            is_active=True,
            is_verified=True,
            discord_username="org1#0001",
            city="Warsaw",
            country="Poland",
        )
        session.add(org1)
        session.commit()
        session.refresh(org1)

        # Create players p1-p30
        players = []
        for i in range(1, 31):
            p = User(
                email=f"p{i}@t.co",
                username=f"p{i}",
                hashed_password=get_password_hash("test"),
                role="player",
                is_active=True,
                is_verified=True,
                discord_username=f"p{i}#{1000+i}",
                city=choice(["Warsaw", "Krakow", "Berlin", "Online"]),
                country=choice(["Poland", "Germany", "UK", "Online"]),
            )
            session.add(p)
            players.append(p)
        session.commit()
        for p in players:
            session.refresh(p)
        print(f"  Created org1 (admin) + {len(players)} players")

        # Initialize ELO for all players
        print("\nInitializing player ELOs...")
        for p in players:
            session.exec(
                text(
                    f"""
                INSERT INTO player_elo (user_id, elo, games_played, k_factor_games, updated_at)
                VALUES ({p.id}, 1000, 0, 0, NOW())
            """
                )
            )
        session.commit()

        # ELO tracking dict
        elos = {p.id: {"elo": 1000, "games": 0, "k_games": 0} for p in players}

        def get_k(user_id):
            return 50 if elos[user_id]["k_games"] < 5 else 32

        def update_elo(u1_id, u2_id, s1, s2):
            e1, e2 = elos[u1_id]["elo"], elos[u2_id]["elo"]
            if s1 > s2:
                r1, r2 = 1.0, 0.0
            elif s1 < s2:
                r1, r2 = 0.0, 1.0
            else:
                r1, r2 = 0.5, 0.5
            c1 = calculate_elo_change(e1, e2, r1, get_k(u1_id))
            c2 = calculate_elo_change(e2, e1, r2, get_k(u2_id))
            elos[u1_id]["elo"] += c1
            elos[u2_id]["elo"] += c2
            elos[u1_id]["games"] += 1
            elos[u2_id]["games"] += 1
            elos[u1_id]["k_games"] += 1
            elos[u2_id]["k_games"] += 1
            return e1, e1 + c1, e2, e2 + c2

        # ======= LEAGUE 1: 8 players, finished =======
        print("\nCreating 8-player FINISHED league...")
        session.exec(
            text(
                f"""
            INSERT INTO leagues (name, description, organizer_id, city, country, registration_end, 
                group_phase_start, group_phase_end, knockout_phase_start, knockout_phase_end,
                status, group_phase_ended, finished_at, min_players, max_players, min_group_size, max_group_size,
                has_knockout_phase, knockout_size, current_knockout_round, has_group_phase_lists, created_at)
            VALUES ('8-Player League (Finished)', 'Small league, 2 groups of 4', {org1.id}, 'Warsaw', 'Poland',
                NOW() - interval '60 days', NOW() - interval '55 days', NOW() - interval '30 days',
                NOW() - interval '25 days', NOW() - interval '5 days',
                'finished', true, NOW() - interval '5 days', 8, 8, 4, 4, true, 4, 'final', true, NOW())
        """
            )
        )
        session.commit()
        league1_id = session.exec(
            text("SELECT id FROM leagues WHERE name = '8-Player League (Finished)'")
        ).first()[0]

        # Groups for league 1
        for gname in ["Group A", "Group B"]:
            session.exec(
                text(
                    f"INSERT INTO groups (league_id, name, created_at) VALUES ({league1_id}, '{gname}', NOW())"
                )
            )
        session.commit()
        g1a = session.exec(
            text(
                f"SELECT id FROM groups WHERE league_id = {league1_id} AND name = 'Group A'"
            )
        ).first()[0]
        g1b = session.exec(
            text(
                f"SELECT id FROM groups WHERE league_id = {league1_id} AND name = 'Group B'"
            )
        ).first()[0]

        # Add 8 players to league 1
        lp1_ids = []
        for i, p in enumerate(players[:8]):
            gid = g1a if i < 4 else g1b
            faction = choice(FACTIONS)
            session.exec(
                text(
                    f"""
                INSERT INTO league_players (league_id, user_id, group_id, is_claimed, discord_username,
                    group_army_faction, group_army_list, knockout_army_faction, games_played, games_won, games_drawn, games_lost, total_points, joined_at)
                VALUES ({league1_id}, {p.id}, {gid}, true, '{p.discord_username}', 
                    '{faction}', '{faction} list...', '{faction}', 0, 0, 0, 0, 0, NOW())
            """
                )
            )
        session.commit()

        lp1_rows = session.exec(
            text(
                f"SELECT id, user_id, group_id FROM league_players WHERE league_id = {league1_id} ORDER BY id"
            )
        ).all()
        lp1_map = {
            r[1]: {"lpid": r[0], "gid": r[2], "pts": 0, "w": 0, "l": 0, "d": 0, "gp": 0}
            for r in lp1_rows
        }

        # Play group matches for league 1
        for gid in [g1a, g1b]:
            g_players = [p for p in players[:8] if lp1_map[p.id]["gid"] == gid]
            for i in range(len(g_players)):
                for j in range(i + 1, len(g_players)):
                    p1, p2 = g_players[i], g_players[j]
                    s1, s2 = randint(55, 82), randint(55, 82)
                    pts1, pts2 = calculate_match_points(s1, s2), calculate_match_points(
                        s2, s1
                    )
                    e1b, e1a, e2b, e2a = update_elo(p1.id, p2.id, s1, s2)

                    lp1_map[p1.id]["pts"] += pts1
                    lp1_map[p2.id]["pts"] += pts2
                    lp1_map[p1.id]["gp"] += 1
                    lp1_map[p2.id]["gp"] += 1
                    if s1 > s2:
                        lp1_map[p1.id]["w"] += 1
                        lp1_map[p2.id]["l"] += 1
                    elif s2 > s1:
                        lp1_map[p1.id]["l"] += 1
                        lp1_map[p2.id]["w"] += 1
                    else:
                        lp1_map[p1.id]["d"] += 1
                        lp1_map[p2.id]["d"] += 1

                    session.exec(
                        text(
                            f"""
                        INSERT INTO matches (league_id, player1_id, player2_id, phase, player1_score, player2_score,
                            player1_league_points, player2_league_points, status, submitted_by_id, confirmed_by_id,
                            submitted_at, confirmed_at, map_name, player1_elo_before, player1_elo_after,
                            player2_elo_before, player2_elo_after, created_at)
                        VALUES ({league1_id}, {lp1_map[p1.id]["lpid"]}, {lp1_map[p2.id]["lpid"]}, 'group',
                            {s1}, {s2}, {pts1}, {pts2}, 'confirmed', {p1.id}, {p2.id},
                            NOW() - interval '{randint(1,5)} days', NOW() - interval '{randint(1,24)} hours',
                            '{choice(MAPS)}', {e1b}, {e1a}, {e2b}, {e2a}, NOW())
                    """
                        )
                    )
        session.commit()

        # Update player stats
        for uid, data in lp1_map.items():
            session.exec(
                text(
                    f"""
                UPDATE league_players SET games_played = {data["gp"]}, games_won = {data["w"]},
                    games_lost = {data["l"]}, games_drawn = {data["d"]}, total_points = {data["pts"]}
                WHERE id = {data["lpid"]}
            """
                )
            )
        session.commit()

        print(f"  Created league with 8 players, all group matches played")

        # ======= LEAGUE 2: 16 players, knockout phase =======
        print("\nCreating 16-player KNOCKOUT league...")
        session.exec(
            text(
                f"""
            INSERT INTO leagues (name, description, organizer_id, city, country, registration_end,
                group_phase_start, group_phase_end, knockout_phase_start,
                status, group_phase_ended, min_players, max_players, min_group_size, max_group_size,
                has_knockout_phase, knockout_size, current_knockout_round, has_group_phase_lists, has_knockout_phase_lists, created_at)
            VALUES ('16-Player League (Knockout)', '4 groups of 4, in knockouts', {org1.id}, 'Berlin', 'Germany',
                NOW() - interval '30 days', NOW() - interval '25 days', NOW() - interval '7 days', NOW() - interval '5 days',
                'knockout_phase', true, 16, 16, 4, 4, true, 8, 'quarter', true, true, NOW())
        """
            )
        )
        session.commit()
        league2_id = session.exec(
            text("SELECT id FROM leagues WHERE name = '16-Player League (Knockout)'")
        ).first()[0]

        # 4 groups
        g2_ids = []
        for gname in ["Group A", "Group B", "Group C", "Group D"]:
            session.exec(
                text(
                    f"INSERT INTO groups (league_id, name, created_at) VALUES ({league2_id}, '{gname}', NOW())"
                )
            )
        session.commit()
        g2_rows = session.exec(
            text(
                f"SELECT id, name FROM groups WHERE league_id = {league2_id} ORDER BY name"
            )
        ).all()
        g2_ids = [r[0] for r in g2_rows]

        # 16 players
        lp2_map = {}
        for i, p in enumerate(players[:16]):
            gid = g2_ids[i // 4]
            faction = choice(FACTIONS)
            session.exec(
                text(
                    f"""
                INSERT INTO league_players (league_id, user_id, group_id, is_claimed, discord_username,
                    group_army_faction, group_army_list, knockout_army_faction, knockout_army_list,
                    games_played, games_won, games_drawn, games_lost, total_points, joined_at)
                VALUES ({league2_id}, {p.id}, {gid}, true, '{p.discord_username}',
                    '{faction}', '{faction} list', '{faction}', '{faction} ko list', 0, 0, 0, 0, 0, NOW())
            """
                )
            )
        session.commit()

        lp2_rows = session.exec(
            text(
                f"SELECT id, user_id, group_id FROM league_players WHERE league_id = {league2_id} ORDER BY id"
            )
        ).all()
        lp2_map = {
            r[1]: {"lpid": r[0], "gid": r[2], "pts": 0, "w": 0, "l": 0, "d": 0, "gp": 0}
            for r in lp2_rows
        }

        # Group matches for league 2
        for gid in g2_ids:
            g_players = [p for p in players[:16] if lp2_map[p.id]["gid"] == gid]
            for i in range(len(g_players)):
                for j in range(i + 1, len(g_players)):
                    p1, p2 = g_players[i], g_players[j]
                    s1, s2 = randint(55, 82), randint(55, 82)
                    pts1, pts2 = calculate_match_points(s1, s2), calculate_match_points(
                        s2, s1
                    )
                    e1b, e1a, e2b, e2a = update_elo(p1.id, p2.id, s1, s2)

                    lp2_map[p1.id]["pts"] += pts1
                    lp2_map[p2.id]["pts"] += pts2
                    lp2_map[p1.id]["gp"] += 1
                    lp2_map[p2.id]["gp"] += 1
                    if s1 > s2:
                        lp2_map[p1.id]["w"] += 1
                        lp2_map[p2.id]["l"] += 1
                    elif s2 > s1:
                        lp2_map[p1.id]["l"] += 1
                        lp2_map[p2.id]["w"] += 1
                    else:
                        lp2_map[p1.id]["d"] += 1
                        lp2_map[p2.id]["d"] += 1

                    session.exec(
                        text(
                            f"""
                        INSERT INTO matches (league_id, player1_id, player2_id, phase, player1_score, player2_score,
                            player1_league_points, player2_league_points, status, submitted_by_id, confirmed_by_id,
                            submitted_at, confirmed_at, map_name, player1_elo_before, player1_elo_after,
                            player2_elo_before, player2_elo_after, created_at)
                        VALUES ({league2_id}, {lp2_map[p1.id]["lpid"]}, {lp2_map[p2.id]["lpid"]}, 'group',
                            {s1}, {s2}, {pts1}, {pts2}, 'confirmed', {p1.id}, {p2.id},
                            NOW() - interval '{randint(8,20)} days', NOW() - interval '{randint(7,14)} days',
                            '{choice(MAPS)}', {e1b}, {e1a}, {e2b}, {e2a}, NOW())
                    """
                        )
                    )
        session.commit()

        # Update player stats
        for uid, data in lp2_map.items():
            session.exec(
                text(
                    f"""
                UPDATE league_players SET games_played = {data["gp"]}, games_won = {data["w"]},
                    games_lost = {data["l"]}, games_drawn = {data["d"]}, total_points = {data["pts"]}
                WHERE id = {data["lpid"]}
            """
                )
            )
        session.commit()

        # Some knockout matches (2 played, 2 scheduled)
        session.exec(
            text(
                f"""
            INSERT INTO matches (league_id, player1_id, player2_id, phase, knockout_round, status, deadline, created_at)
            SELECT {league2_id}, 
                (SELECT id FROM league_players WHERE league_id = {league2_id} LIMIT 1 OFFSET 0),
                (SELECT id FROM league_players WHERE league_id = {league2_id} LIMIT 1 OFFSET 7),
                'knockout', 'quarter', 'scheduled', NOW() + interval '7 days', NOW()
        """
            )
        )
        session.exec(
            text(
                f"""
            INSERT INTO matches (league_id, player1_id, player2_id, phase, knockout_round, status, deadline, created_at)
            SELECT {league2_id},
                (SELECT id FROM league_players WHERE league_id = {league2_id} LIMIT 1 OFFSET 1),
                (SELECT id FROM league_players WHERE league_id = {league2_id} LIMIT 1 OFFSET 6),
                'knockout', 'quarter', 'scheduled', NOW() + interval '7 days', NOW()
        """
            )
        )
        session.commit()

        print(f"  Created league with 16 players, all group matches, 2 KO scheduled")

        # ======= LEAGUE 3: 12 players, group phase =======
        print("\nCreating 12-player GROUP PHASE league...")
        session.exec(
            text(
                f"""
            INSERT INTO leagues (name, description, organizer_id, city, country, registration_end, group_phase_start,
                status, min_players, max_players, min_group_size, max_group_size,
                has_knockout_phase, knockout_size, has_group_phase_lists, created_at)
            VALUES ('12-Player League (Group Phase)', '2 groups of 6, in progress', {org1.id}, 'London', 'UK',
                NOW() - interval '14 days', NOW() - interval '10 days',
                'group_phase', 12, 12, 6, 6, true, 8, true, NOW())
        """
            )
        )
        session.commit()
        league3_id = session.exec(
            text("SELECT id FROM leagues WHERE name = '12-Player League (Group Phase)'")
        ).first()[0]

        # 2 groups
        for gname in ["Group A", "Group B"]:
            session.exec(
                text(
                    f"INSERT INTO groups (league_id, name, created_at) VALUES ({league3_id}, '{gname}', NOW())"
                )
            )
        session.commit()
        g3_rows = session.exec(
            text(f"SELECT id FROM groups WHERE league_id = {league3_id} ORDER BY name")
        ).all()
        g3a, g3b = g3_rows[0][0], g3_rows[1][0]

        # 12 players (using p6-p17)
        for i, p in enumerate(players[5:17]):
            gid = g3a if i < 6 else g3b
            faction = choice(FACTIONS)
            session.exec(
                text(
                    f"""
                INSERT INTO league_players (league_id, user_id, group_id, is_claimed, discord_username,
                    group_army_faction, group_army_list, games_played, total_points, joined_at)
                VALUES ({league3_id}, {p.id}, {gid}, true, '{p.discord_username}',
                    '{faction}', '{faction} list', 0, 0, NOW())
            """
                )
            )
        session.commit()

        # Some matches played (8/15 per group)
        lp3_rows = session.exec(
            text(
                f"SELECT id, user_id, group_id FROM league_players WHERE league_id = {league3_id}"
            )
        ).all()
        lp3_map = {r[1]: {"lpid": r[0], "gid": r[2]} for r in lp3_rows}

        for gid in [g3a, g3b]:
            g_uids = [uid for uid, d in lp3_map.items() if d["gid"] == gid]
            match_count = 0
            for i in range(len(g_uids)):
                for j in range(i + 1, len(g_uids)):
                    if match_count < 8:
                        s1, s2 = randint(55, 82), randint(55, 82)
                        session.exec(
                            text(
                                f"""
                            INSERT INTO matches (league_id, player1_id, player2_id, phase,
                                player1_score, player2_score, status, map_name, created_at)
                            VALUES ({league3_id}, {lp3_map[g_uids[i]]["lpid"]}, {lp3_map[g_uids[j]]["lpid"]}, 'group',
                                {s1}, {s2}, 'confirmed', '{choice(MAPS)}', NOW())
                        """
                            )
                        )
                    else:
                        session.exec(
                            text(
                                f"""
                            INSERT INTO matches (league_id, player1_id, player2_id, phase, status, deadline, created_at)
                            VALUES ({league3_id}, {lp3_map[g_uids[i]]["lpid"]}, {lp3_map[g_uids[j]]["lpid"]}, 'group',
                                'scheduled', NOW() + interval '{randint(3,14)} days', NOW())
                        """
                            )
                        )
                    match_count += 1
        session.commit()
        print(f"  Created league with 12 players, partially played")

        # ======= LEAGUE 4: 20 players, registration =======
        print("\nCreating 20-player REGISTRATION league...")
        session.exec(
            text(
                f"""
            INSERT INTO leagues (name, description, organizer_id, city, country, registration_end,
                status, min_players, max_players, min_group_size, max_group_size,
                has_knockout_phase, knockout_size, has_group_phase_lists, has_knockout_phase_lists, created_at)
            VALUES ('20-Player League (Registration)', '4 groups of 5, sign up now!', {org1.id}, 'Online', 'Online',
                NOW() + interval '5 days',
                'registration', 20, 20, 5, 5, true, 8, true, true, NOW())
        """
            )
        )
        session.commit()
        league4_id = session.exec(
            text(
                "SELECT id FROM leagues WHERE name = '20-Player League (Registration)'"
            )
        ).first()[0]

        # 15 players registered (p11-p25)
        for p in players[10:25]:
            session.exec(
                text(
                    f"""
                INSERT INTO league_players (league_id, user_id, is_claimed, discord_username, games_played, total_points, joined_at)
                VALUES ({league4_id}, {p.id}, true, '{p.discord_username}', 0, 0, NOW())
            """
                )
            )
        session.commit()
        print(f"  Created league with 15/20 players registered")

        # ======= LEAGUE 5: 6 players, no knockout, finished =======
        print("\nCreating 6-player NO KNOCKOUT league...")
        session.exec(
            text(
                f"""
            INSERT INTO leagues (name, description, organizer_id, city, country, registration_end,
                group_phase_start, group_phase_end, status, group_phase_ended, finished_at,
                min_players, max_players, min_group_size, max_group_size, has_knockout_phase, created_at)
            VALUES ('6-Player Casual (No Knockout)', 'Single group, completed', {org1.id}, 'Krakow', 'Poland',
                NOW() - interval '40 days', NOW() - interval '35 days', NOW() - interval '10 days',
                'finished', true, NOW() - interval '10 days',
                6, 6, 6, 6, false, NOW())
        """
            )
        )
        session.commit()
        league5_id = session.exec(
            text("SELECT id FROM leagues WHERE name = '6-Player Casual (No Knockout)'")
        ).first()[0]

        # Single group
        session.exec(
            text(
                f"INSERT INTO groups (league_id, name, created_at) VALUES ({league5_id}, 'Group A', NOW())"
            )
        )
        session.commit()
        g5_id = session.exec(
            text(f"SELECT id FROM groups WHERE league_id = {league5_id}")
        ).first()[0]

        # 6 players (p21-p26)
        for p in players[20:26]:
            session.exec(
                text(
                    f"""
                INSERT INTO league_players (league_id, user_id, group_id, is_claimed, discord_username, games_played, total_points, joined_at)
                VALUES ({league5_id}, {p.id}, {g5_id}, true, '{p.discord_username}', 0, 0, NOW())
            """
                )
            )
        session.commit()

        # All matches played
        lp5_rows = session.exec(
            text(
                f"SELECT id, user_id FROM league_players WHERE league_id = {league5_id}"
            )
        ).all()
        lp5_ids = [r[0] for r in lp5_rows]
        for i in range(6):
            for j in range(i + 1, 6):
                s1, s2 = randint(55, 82), randint(55, 82)
                session.exec(
                    text(
                        f"""
                    INSERT INTO matches (league_id, player1_id, player2_id, phase,
                        player1_score, player2_score, status, map_name, created_at)
                    VALUES ({league5_id}, {lp5_ids[i]}, {lp5_ids[j]}, 'group',
                        {s1}, {s2}, 'confirmed', '{choice(MAPS)}', NOW())
                """
                    )
                )
        session.commit()
        print(f"  Created league with 6 players, all matches played")

        # Update all ELOs in database
        print("\nUpdating ELO records...")
        for uid, data in elos.items():
            session.exec(
                text(
                    f"""
                UPDATE player_elo SET elo = {data["elo"]}, games_played = {data["games"]}, 
                    k_factor_games = {data["k_games"]}, updated_at = NOW()
                WHERE user_id = {uid}
            """
                )
            )
        session.commit()

        # Create matchups
        print("\nCreating matchups...")
        matchups_data = [
            ("fresh-001", players[0].id, players[1].id, False, False, None, None),
            (
                "waiting-002",
                players[2].id,
                players[3].id,
                True,
                False,
                "Stormcast army...",
                None,
            ),
        ]
        for name, p1, p2, sub1, sub2, list1, list2 in matchups_data:
            session.exec(
                text(
                    f"""
                INSERT INTO matchups (name, player1_id, player2_id, player1_submitted, player2_submitted, 
                    player1_list, player2_list, created_at)
                VALUES ('{name}', {p1}, {p2}, {str(sub1).lower()}, {str(sub2).lower()}, 
                    {f"'{list1}'" if list1 else 'NULL'}, {f"'{list2}'" if list2 else 'NULL'}, NOW())
            """
                )
            )
        session.commit()
        print("  Created 2 matchups")

        # Print rankings
        print("\n" + "=" * 60)
        print("TOP 15 ELO RANKINGS")
        print("=" * 60)
        sorted_elos = sorted(elos.items(), key=lambda x: x[1]["elo"], reverse=True)
        for i, (uid, data) in enumerate(sorted_elos[:15], 1):
            user = session.get(User, uid)
            print(
                f"  {i:2}. {user.username:6} - ELO: {data['elo']:4} ({data['games']} games)"
            )

        print("\n" + "=" * 60)
        print("DONE!")
        print("=" * 60)
        print("\nCredentials: org1 / p1-p30 : test")
        print("\nLeagues:")
        print("  - 8-player (finished)")
        print("  - 16-player (knockout phase)")
        print("  - 12-player (group phase)")
        print("  - 20-player (registration)")
        print("  - 6-player (no knockout, finished)")
        print()


if __name__ == "__main__":
    main()

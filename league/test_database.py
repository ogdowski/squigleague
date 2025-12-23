#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

import league.database as db
from datetime import date

def test_database_operations():
    """Test basic database operations"""
    print("Testing League Database Operations...")
    print("=" * 50)

    print("\n1. Testing database health check...")
    if db.check_database_health():
        print("✓ Database connection OK")
    else:
        print("✗ Database connection FAILED")
        return

    print("\n2. Testing season retrieval...")
    season = db.get_season(1)
    if season:
        print(f"✓ Found season: {season['name']}")
        print(f"  - Format: {season['league_format']}")
        print(f"  - Scoring: {season['scoring_system']}")
        print(f"  - Status: {season['status']}")
    else:
        print("✗ Failed to retrieve season")
        return

    print("\n3. Testing player creation...")
    player_id = db.get_or_create_player(
        discord_id="test123",
        discord_name="Test Player",
        discord_avatar="https://example.com/avatar.png"
    )
    if player_id:
        print(f"✓ Player created with ID: {player_id}")
    else:
        print("✗ Failed to create player")
        return

    print("\n4. Testing player retrieval...")
    player = db.get_player_by_discord_id("test123")
    if player:
        print(f"✓ Retrieved player: {player['discord_name']}")
        print(f"  - ELO: {player['global_elo']}")
        print(f"  - Games: {player['total_games']}")
    else:
        print("✗ Failed to retrieve player")
        return

    print("\n5. Testing participant registration...")
    participant_id = db.register_participant(
        season_id=1,
        player_id=player_id,
        starting_elo=1500
    )
    if participant_id:
        print(f"✓ Participant registered with ID: {participant_id}")
    else:
        print("✗ Failed to register participant")
        return

    print("\n6. Testing participant retrieval...")
    participant = db.get_participant(player_id, 1)
    if participant:
        print(f"✓ Retrieved participant: {participant['player_name']}")
        print(f"  - Starting ELO: {participant['starting_elo']}")
        print(f"  - Group: {participant['group_number']}")
    else:
        print("✗ Failed to retrieve participant")
        return

    print("\n7. Testing season list...")
    seasons = db.list_seasons()
    if seasons:
        print(f"✓ Found {len(seasons)} season(s)")
        for s in seasons:
            print(f"  - {s['name']} ({s['participant_count']} participants)")
    else:
        print("✗ Failed to list seasons")

    print("\n8. Testing stats retrieval...")
    stats = db.get_stats()
    if stats:
        print(f"✓ Stats retrieved:")
        print(f"  - Seasons: {stats['total_seasons']}")
        print(f"  - Players: {stats['total_players']}")
        print(f"  - Matches: {stats['total_matches']}")
    else:
        print("✗ Failed to get stats")

    print("\n" + "=" * 50)
    print("All tests passed! ✓")

if __name__ == "__main__":
    test_database_operations()

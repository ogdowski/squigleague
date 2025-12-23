from typing import List, Dict, Any, Optional, Tuple
import random
import logging
from league.services.base import BaseFormatHandler
import league.database as db

logger = logging.getLogger(__name__)

class GroupPlayoffHandler(BaseFormatHandler):
    """
    Group + Playoff format handler.

    Phase flow:
    1. registration -> Group assignment
    2. group_phase -> Round-robin within groups
    3. playoffs -> Top players from groups compete
    4. completed -> Final rankings determined

    Expected config:
    {
        "num_groups": 4,
        "max_unplayed_games": 1,
        "use_elo_for_grouping": false
    }
    """

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        if "num_groups" not in self.config:
            return False, "num_groups required in format_config"

        if self.config["num_groups"] < 2:
            return False, "num_groups must be at least 2"

        return True, None

    def initialize_season(self, participants: List[dict]) -> bool:
        """Assign players to groups"""
        try:
            num_groups = self.config["num_groups"]
            use_elo = self.config.get("use_elo_for_grouping", False)

            if use_elo:
                participants.sort(key=lambda p: p['starting_elo'], reverse=True)
            else:
                random.shuffle(participants)

            for i, participant in enumerate(participants):
                group_num = (i % num_groups) + 1
                db.update_participant_group(participant['id'], group_num)

            return True
        except Exception as e:
            logger.error(f"Error initializing season: {e}")
            return False

    def get_next_matches(self) -> List[Dict[str, Any]]:
        """Get upcoming matches in group phase"""
        if self.season['status'] != "group_phase":
            return []

        upcoming_matches = []
        num_groups = self.config["num_groups"]

        for group_num in range(1, num_groups + 1):
            participants = db.get_group_participants(self.season['id'], group_num)

            for i, p1 in enumerate(participants):
                for p2 in participants[i+1:]:
                    upcoming_matches.append({
                        "player1_id": p1['player_id'],
                        "player2_id": p2['player_id'],
                        "group_number": group_num,
                        "phase": "group"
                    })

        return upcoming_matches

    def record_match_result(self, match: dict, participant1: dict, participant2: dict) -> bool:
        """Update participant standings after match"""
        try:
            db.update_participant_stats(
                participant1['id'],
                match['player1_points'],
                match['player1_score']
            )
            db.update_participant_stats(
                participant2['id'],
                match['player2_points'],
                match['player2_score']
            )
            return True
        except Exception as e:
            logger.error(f"Error recording match result: {e}")
            return False

    def get_standings(self) -> Dict[str, Any]:
        """Get group standings"""
        num_groups = self.config["num_groups"]
        standings = {}

        for group_num in range(1, num_groups + 1):
            participants = db.get_group_participants(self.season['id'], group_num)
            participants.sort(key=lambda p: p['group_points'], reverse=True)

            standings[f"group_{group_num}"] = [
                {
                    "position": i + 1,
                    "player_id": p['player_id'],
                    "player_name": p['player_name'],
                    "points": p['group_points'],
                    "games_played": p['group_games_played'],
                    "avg_score": float(p['group_avg_score'] or 0),
                    "current_elo": p['current_season_elo']
                }
                for i, p in enumerate(participants)
            ]

        return {
            "type": "group_standings",
            "groups": standings
        }

    def can_advance_phase(self) -> Tuple[bool, Optional[str]]:
        """Check if can advance to next phase"""
        if self.season['status'] != "group_phase":
            return False, f"Current status is {self.season['status']}, not group_phase"

        max_unplayed = self.config.get("max_unplayed_games", 1)
        num_groups = self.config["num_groups"]

        for group_num in range(1, num_groups + 1):
            participants = db.get_group_participants(self.season['id'], group_num)
            group_size = len(participants)
            max_games = group_size - 1

            for p in participants:
                unplayed = max_games - p['group_games_played']
                if unplayed > max_unplayed:
                    return False, (
                        f"Player {p['player_name']} in group {group_num} "
                        f"has {unplayed} unplayed games (max allowed: {max_unplayed})"
                    )

        return True, None

    def advance_phase(self) -> str:
        """Advance to next phase"""
        if self.season['status'] == "registration":
            return "group_phase"
        elif self.season['status'] == "group_phase":
            return "playoffs"
        elif self.season['status'] == "playoffs":
            return "completed"
        return self.season['status']

    def determine_final_rankings(self) -> List[Dict[str, Any]]:
        """Determine final rankings"""
        return []

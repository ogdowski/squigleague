"""Test the battle plan randomizer"""

import sys
from pathlib import Path

# Add squire to path
sys.path.insert(0, str(Path(__file__).parent))

from squire.battle_plans import generate_battle_plan, GameSystem, format_battle_plan


def test_all_systems():
    """Generate battle plans for all supported systems"""

    print("\n" + "=" * 60)
    print("BATTLE PLAN RANDOMIZER TEST")
    print("=" * 60 + "\n")

    systems = [
        (GameSystem.AOS, "Age of Sigmar"),
        (GameSystem.WARHAMMER_40K, "Warhammer 40,000"),
        (GameSystem.OLD_WORLD, "The Old World"),
    ]

    for system, name in systems:
        print(f"\n{'#'*60}")
        print(f"# {name}")
        print(f"{'#'*60}\n")

        # Generate 2 random plans for each system
        for i in range(2):
            plan = generate_battle_plan(system)
            print(format_battle_plan(plan))
            print()


if __name__ == "__main__":
    test_all_systems()

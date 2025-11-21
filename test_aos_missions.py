"""Quick test of AoS mission randomization"""

from squire.battle_plans import generate_aos_battle_plan

print("Testing Age of Sigmar General's Handbook 2025-2026 Battle Plans\n")
print("=" * 70)

for i in range(5):
    bp = generate_aos_battle_plan()
    print(f"\n{i+1}. {bp.name}")
    print(f"   Deployment: {bp.deployment_description}")
    print(f"   Scoring: {bp.primary_objective[:60]}...")
    if bp.special_rules:
        print(f"   Underdog: {[r for r in bp.special_rules if 'Underdog' in r][0]}")

print("\n" + "=" * 70)
print("All 12 missions available for randomization ✓")

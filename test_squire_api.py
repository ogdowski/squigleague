"""
Test script to verify Squire battle plan API is working correctly
Tests all 12 AoS missions are present and returning valid data
"""

import json
from collections import Counter

import requests

BASE_URL = "http://localhost:8000"
HEADERS = {"User-Agent": "Squire-Test-Suite/1.0"}


def test_api_health():
    """Test basic API connectivity"""
    print("\n" + "=" * 70)
    print("Testing API Health...")
    print("=" * 70)

    try:
        response = requests.get(
            f"{BASE_URL}/api/squire/health", headers=HEADERS, timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data}")
            return True
        else:
            print(f"❌ API Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("\nMake sure Docker is running: docker-compose up -d")
        return False


def test_aos_missions():
    """Test Age of Sigmar mission randomization"""
    print("\n" + "=" * 70)
    print("Testing Age of Sigmar Battle Plans...")
    print("=" * 70)

    expected_missions = {
        "Passing Seasons",
        "Paths of the Fey",
        "Roiling Roots",
        "Cyclic Shifts",
        "Surge of Slaughter",
        "Linked Ley Lines",
        "Noxious Nexus",
        "The Liferoots",
        "Bountiful Equinox",
        "Lifecycle",
        "Creeping Corruption",
        "Grasp of Thorns",
    }

    found_missions = set()
    mission_details = {}

    # Generate 50 random missions to ensure we see all 12
    print(f"\nGenerating 50 random missions to find all 12...")
    for i in range(50):
        try:
            response = requests.get(
                f"{BASE_URL}/api/squire/battle-plan/random",
                params={"system": "age_of_sigmar"},
                headers=HEADERS,
                timeout=5,
            )

            if response.status_code == 200:
                data = response.json()
                mission_name = data.get("name")
                found_missions.add(mission_name)

                if mission_name not in mission_details:
                    mission_details[mission_name] = data
            else:
                print(f"❌ Request {i+1} failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Request {i+1} error: {e}")

    print(f"\n✅ Found {len(found_missions)} unique missions:")
    for mission in sorted(found_missions):
        print(f"   - {mission}")

    # Check if all expected missions were found
    missing = expected_missions - found_missions
    extra = found_missions - expected_missions

    if missing:
        print(f"\n❌ Missing missions: {missing}")

    if extra:
        print(f"\n⚠️  Unexpected missions: {extra}")

    if not missing and not extra:
        print(f"\n✅ All 12 General's Handbook 2025-2026 missions present!")

    # Display sample mission details
    print("\n" + "=" * 70)
    print("Sample Mission Details:")
    print("=" * 70)

    if mission_details:
        sample = list(mission_details.values())[0]
        print(f"\nMission: {sample['name']}")
        print(f"Deployment: {sample['deployment_description']}")
        print(f"Scoring: {sample['primary_objective']}")
        print(f"Victory Conditions: {sample['victory_conditions']}")
        print(f"Special Rules:")
        for rule in sample.get("special_rules", []):
            print(f"  - {rule}")

    return len(found_missions) == 12


def test_multiple_plans():
    """Test generating multiple battle plans for tournaments"""
    print("\n" + "=" * 70)
    print("Testing Tournament Mode (Multiple Plans)...")
    print("=" * 70)

    try:
        response = requests.get(
            f"{BASE_URL}/api/squire/battle-plan/multiple",
            params={"system": "age_of_sigmar", "count": 5},
            headers=HEADERS,
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generated {len(data)} tournament rounds:")
            for i, plan in enumerate(data, 1):
                print(f"   Round {i}: {plan['name']}")
            return True
        else:
            print(f"❌ Multiple plans request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_systems_endpoint():
    """Test the systems information endpoint"""
    print("\n" + "=" * 70)
    print("Testing Game Systems Endpoint...")
    print("=" * 70)

    try:
        response = requests.get(
            f"{BASE_URL}/api/squire/systems", headers=HEADERS, timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available game systems:")
            for system in data:
                print(f"   - {system['game_system']}: {system['description']}")
            return True
        else:
            print(f"❌ Systems request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# SQUIRE MODULE TEST SUITE")
    print("# Testing General's Handbook 2025-2026 Battle Plans")
    print("#" * 70)

    results = []

    # Run all tests
    results.append(("API Health", test_api_health()))

    if results[0][1]:  # Only continue if API is healthy
        results.append(("AoS Missions (12 total)", test_aos_missions()))
        results.append(("Tournament Mode", test_multiple_plans()))
        results.append(("Systems Endpoint", test_systems_endpoint()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Squire module is working correctly.")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check output above for details.")
        exit(1)

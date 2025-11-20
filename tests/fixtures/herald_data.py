"""
Sample Herald test data

Pre-defined test data for common testing scenarios.
"""

import hashlib
from datetime import datetime

# ═══════════════════════════════════════════════
# SAMPLE ARMY LISTS
# ═══════════════════════════════════════════════

SAMPLE_LIST_SPACE_MARINES = """
Space Marines - Ultramarines
1000 points

HQ:
- Captain with Power Sword and Plasma Pistol (90pts)
- Librarian with Force Sword (80pts)

Troops:
- 10x Intercessor Squad with Bolt Rifles (200pts)
- 10x Tactical Marines with Flamer and Missile Launcher (180pts)

Elites:
- 5x Terminators with Storm Bolters and Power Fists (200pts)

Heavy Support:
- Predator Tank with Autocannon and Lascannons (150pts)
- Devastator Squad with 4x Lascannons (100pts)

Total: 1000pts
"""

SAMPLE_LIST_ORKS = """
Orks - Goffs Clan
1000 points

HQ:
- Warboss with Power Klaw and Kombi-Skorcha (100pts)
- Big Mek with Shokk Attack Gun (80pts)

Troops:
- 20x Boyz with Sluggas and Choppas (180pts)
- 20x Boyz with Sluggas and Choppas (180pts)
- 10x Gretchin (40pts)

Elites:
- 5x Nobz with Big Choppas (100pts)

Fast Attack:
- 3x Deffkoptas with Twin Rokkits (150pts)

Heavy Support:
- Battlewagon with Killkannon (170pts)

Total: 1000pts
"""

SAMPLE_LIST_NECRONS = """
Necrons - Sautekh Dynasty
1000 points

HQ:
- Overlord with Warscythe (90pts)
- Cryptek with Canoptek Cloak (90pts)

Troops:
- 20x Necron Warriors (260pts)
- 10x Immortals with Tesla Carbines (170pts)

Elites:
- 5x Lychguard with Hyperphase Swords (190pts)

Fast Attack:
- 3x Canoptek Scarabs (60pts)

Heavy Support:
- Doomsday Ark (140pts)

Total: 1000pts
"""

SAMPLE_LIST_MINIMAL = "Test Army List\n500 points"

SAMPLE_LIST_EMPTY = ""

SAMPLE_LIST_TOO_LONG = "X" * 50001  # Exceeds 50k character limit

# ═══════════════════════════════════════════════
# SAMPLE EXCHANGE IDs
# ═══════════════════════════════════════════════

VALID_EXCHANGE_IDS = [
    "crimson-marine-charges-7a2f",
    "void-necron-awakens-b3e1",
    "blessed-captain-purges-4d2c",
    "ancient-farseer-teleports-9c4d",
    "cursed-daemon-manifests-1f8e",
    "iron-warboss-waaagh-3a7b",
]

INVALID_EXCHANGE_IDS = [
    "invalid",  # Wrong format
    "too-short",  # Not enough parts
    "invalid-word-charges-7a2f",  # Invalid adjective
    "crimson-invalid-charges-7a2f",  # Invalid noun
    "crimson-marine-invalid-7a2f",  # Invalid verb
    "crimson-marine-charges-ZZZZ",  # Invalid hash (not hex)
    "crimson-marine-charges-7a",  # Hash too short
    "crimson-marine-charges-7a2f11",  # Hash too long
]

# ═══════════════════════════════════════════════
# SAMPLE EXCHANGES
# ═══════════════════════════════════════════════

def create_sample_exchange(
    exchange_id: str = "test-exchange-0001",
    list_a: str = SAMPLE_LIST_SPACE_MARINES,
    list_b: str = None
):
    """Create sample exchange dict"""
    hash_a = hashlib.sha256(list_a.strip().encode()).hexdigest()
    
    exchange = {
        "id": exchange_id,
        "list_a": list_a.strip(),
        "hash_a": hash_a,
        "timestamp_a": datetime.now(),
        "list_b": None,
        "hash_b": None,
        "timestamp_b": None
    }
    
    if list_b:
        hash_b = hashlib.sha256(list_b.strip().encode()).hexdigest()
        exchange["list_b"] = list_b.strip()
        exchange["hash_b"] = hash_b
        exchange["timestamp_b"] = datetime.now()
    
    return exchange


SAMPLE_PENDING_EXCHANGE = create_sample_exchange(
    exchange_id="crimson-marine-charges-7a2f",
    list_a=SAMPLE_LIST_SPACE_MARINES,
    list_b=None
)

SAMPLE_COMPLETE_EXCHANGE = create_sample_exchange(
    exchange_id="void-necron-awakens-b3e1",
    list_a=SAMPLE_LIST_SPACE_MARINES,
    list_b=SAMPLE_LIST_ORKS
)

# ═══════════════════════════════════════════════
# SAMPLE REQUEST LOGS
# ═══════════════════════════════════════════════

SAMPLE_IPS = [
    "192.168.1.100",
    "10.0.0.50",
    "172.16.0.25",
    "203.0.113.42",  # TEST-NET-3 (documentation IP)
]

SAMPLE_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "curl/7.68.0",
    "Python/3.11 httpx/0.26.0",
]

BLOCKED_USER_AGENTS = [
    "wget/1.20.3",
    "python-requests/2.28.0",
    "scrapy/2.5.0",
    "beautifulsoup/4.9.3",
]

ALLOWED_BOT_USER_AGENTS = [
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
]

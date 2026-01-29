# BSData Refactor Plan

## Goal
Unify AoR as normal factions, add PrayerLore model, upgrade CoreAbility, clean up model hierarchy.

## Research Findings

### 1. Armies of Renown (AoR) XML Structure
- AoR are **separate .cat files** (e.g. `Kharadron Overlords - Grundstok Expeditionary Force.cat`, `Stormcast Eternals - Ruination Brotherhood.cat`)
- Each AoR .cat has `<catalogueLinks>` referencing the parent faction catalog AND the Library catalog
- AoR catalogs have their own:
  - `<sharedSelectionEntries>` with "Battle Traits: ..." section (own battle traits)
  - `<sharedSelectionEntryGroups>` with "Battle Formations: ...", "Heroic Traits", "Artefacts of Power", "Spell Lores", "Prayer Lores" etc.
  - `<entryLinks>` referencing specific units from the parent Library (this is how unit availability is controlled)
- AoR are structurally identical to normal faction catalogs - they just reference a subset of units and override enhancements

### 2. Core Abilities
- Use profile type `Ability (Passive)` (typeId: `907f-a48-6a04-f788`)
- Have: Effect, Keywords (usually empty), Color attribute, Type attribute
- Do NOT have: Timing, Declare, Casting/Chanting Value
- Colors used: Gray (Fly), Black (Ward Save, Guarded Hero), Purple (Beast)
- Currently parsed with `_parse_ability_profile()` which already extracts all these fields
- **Action**: Make CoreAbility inherit from AbilityBase. It will just have timing/declare as None.

### 3. Prayer Lores vs Spell Lores
- Both live in `Lores.cat` file
- Structurally identical: Timing, Value, Declare, Effect, Keywords + Color/Type attributes
- Only difference: profile typeId and "Casting Value" vs "Chanting Value" field name
- Currently prayers are stored as SpellLore/Spell models (the parser's `_parse_prayer_profile()` maps Chanting Value -> casting_value)
- **Action**: Create separate PrayerLore/Prayer models mirroring SpellLore/Spell

## Refactor Steps

### Step 1: Faction model changes
- Add `is_aor: bool = Field(default=False)` to Faction
- Add `parent_faction_id: Optional[int] = Field(default=None, foreign_key="bsdata_factions.id")` to Faction
- Add relationship: `parent_faction: Optional["Faction"]` and `aor_factions: list["Faction"]`
- Add `battle_formations` relationship (already done)
- AoR factions get: is_aor=True, parent_faction_id=parent's id

### Step 2: Remove ArmyOfRenown and AoRBattleTrait models
- Delete `ArmyOfRenown` model, `AoRBattleTrait` model
- Delete `bsdata_armies_of_renown` and `bsdata_aor_battle_traits` tables
- Remove from Faction.armies_of_renown relationship
- Remove all AoR-specific schemas, routes, sync methods
- AoR battle traits become regular BattleTrait entries on the AoR faction

### Step 3: AoR unit availability
- AoR .cat files have `<entryLinks>` referencing specific units from parent Library
- Need a link table: `bsdata_aor_available_units` (faction_id FK, unit_id FK)
- Units stay on parent faction (unit.faction_id = parent)
- AoR faction references available units via link table
- Frontend: when viewing AoR faction, show units from link table instead of faction's own units
- Parser: extract entryLink names from AoR catalog, match to unit names in parent faction

### Step 4: PrayerLore / Prayer models
- Create `PrayerLore(SQLModel, table=True)` mirroring SpellLore: id, bsdata_id, faction_id, name, points
- Create `Prayer(AbilityBase, table=True)`: id, bsdata_id, lore_id, name, chanting_value, effect, keywords (inherits timing/declare/color from AbilityBase... actually prayers don't need full AbilityBase, they need casting_value equivalent)
- Actually Prayer structure: id, bsdata_id, lore_id, name, chanting_value (str), effect, keywords - same as Spell but with chanting_value instead of casting_value
- Add Faction.prayer_lores relationship
- Schemas: PrayerLoreResponse, PrayerResponse (mirror SpellLoreResponse, SpellResponse)
- Routes: `/factions/{id}/prayer-lores`
- Parser: already has `_parse_prayer_profile()` returning chanting_value as casting_value. Could keep storing as casting_value or rename to chanting_value
- Sync: add `_upsert_faction_prayer_lore()` separate from spell lore
- Stop storing prayers as SpellLore entries

### Step 5: CoreAbility inherits AbilityBase
- Change `class CoreAbility(SQLModel, table=True)` to `class CoreAbility(AbilityBase, table=True)`
- Remove `effect` and `keywords` fields (inherited from AbilityBase)
- Keep `ability_type` field
- Add timing, declare, color columns to bsdata_core_abilities table (migration)
- Update CoreAbilityResponse schema to inherit from AbilityResponseBase

### Step 6: Parser changes
- `parse_faction_main_catalog()`: already handles normal factions. Need same logic for AoR .cat files
- New method or reuse: `parse_aor_catalog()` that:
  - Extracts battle traits, formations, heroic traits, artefacts, spell/prayer/manifestation lore refs
  - Extracts unit entryLinks (names) for unit availability
- `_full_sync()` in sync.py: iterate AoR catalogs separately, create Faction with is_aor=True

### Step 7: Sync changes
- Detect AoR catalogs by filename pattern: `{FactionName} - {AoRName}.cat` (not Library)
- Create AoR as Faction(is_aor=True, parent_faction_id=parent.id)
- Sync battle traits, formations, heroic traits, artefacts, lores to AoR faction using same upsert methods
- Sync unit availability: match entryLink names to Unit records in parent faction, create link table entries

### Step 8: Schema/Route changes
- FactionListItem: add `is_aor: bool`, `parent_faction_id: Optional[int]`
- FactionFull: add `prayer_lores`, `is_aor`, `parent_faction_name`
- New route or filter: `/factions?is_aor=false` (default) to hide AoR from main list
- `/factions/{id}` works for both normal and AoR factions
- AoR faction detail shows available units (from link table) instead of own units

### Step 9: Frontend changes
- Faction list: filter out is_aor factions (they appear inside parent faction's detail page)
- Faction detail: show "Armies of Renown" section listing AoR sub-factions with links
- AoR faction detail: show parent faction link, available units, own traits/formations/lores
- Prayer lores section similar to spell lores section
- Add i18n keys for prayer lores

### Step 10: Migration
- Squash into single migration since not in production:
  - Add is_aor, parent_faction_id to bsdata_factions
  - Create bsdata_aor_available_units link table
  - Create bsdata_prayer_lores table
  - Create bsdata_prayers table
  - Add timing, declare, color to bsdata_core_abilities
  - Drop bsdata_armies_of_renown, bsdata_aor_battle_traits tables

## Files to modify
- `backend/app/bsdata/models.py` - Faction fields, remove AoR models, add PrayerLore/Prayer, CoreAbility inherits AbilityBase
- `backend/app/bsdata/parser.py` - AoR catalog parsing, prayer lore separation
- `backend/app/bsdata/sync.py` - AoR sync as factions, prayer lore sync, remove old AoR sync
- `backend/app/bsdata/schemas.py` - Faction schema updates, PrayerLore schemas, remove AoR schemas
- `backend/app/bsdata/routes.py` - Prayer lore routes, AoR filter on faction list, remove AoR routes
- `backend/migrations/versions/` - New squashed migration
- `frontend/src/components/rules/FactionDetail.vue` - AoR section, prayer lores section
- `frontend/src/components/rules/FactionList.vue` or equivalent - filter AoR
- `frontend/src/locales/en.json` and `pl.json` - prayer lore translations

## Open questions
- Should AoR factions appear in the same grand alliance grouping as their parent?
- Should the URL for AoR be `/rules/faction/{aor_id}` (same as normal) or `/rules/faction/{parent_id}/aor/{aor_id}`?
- For unit availability: do we show the full unit detail (weapons, abilities) or just a name list?

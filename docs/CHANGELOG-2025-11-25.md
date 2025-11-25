# SquigLeague - Documentation & UX Fixes

## Date: 2025-11-25

## Changes Made

### 1. Documentation Structure Created

Created comprehensive documentation in `docs/` directory:

#### A. User Stories (`docs/user-stories.md`)
**Purpose**: Define all features before implementation

**Key Stories Documented**:
- **US-001 to US-005**: Herald tournament administration (planned)
  - Tournament creation, player registration, list submission
  - Automated pairing generation
  - Score submission and standings
  
- **US-006 to US-008**: Battle Plan Integration with Tournaments (planned)
  - System selection during list submission
  - **Automatic battle plan generation when both players submit lists**
  - Matchup summary showing opponents, lists, and battle plan
  
- **US-009**: Battle Plan Reference Tool (implemented)
  - Current standalone tool for practice and reference
  - NOT the tournament integration feature
  
- **US-020 to US-022**: User authentication (planned)
- **US-030 to US-031**: Additional player tools (planned)

**Status Definitions**: Planned | In Progress | Implemented | Released
**Priority Levels**: Critical | High | Medium | Low

#### B. RAID Log (`docs/raid-log.md`)
**Purpose**: Track project risks, assumptions, issues, and dependencies

**Current Items**:
- **Risks**: Docker licensing, third-party API dependency
- **Assumptions**: Modern browsers, GW standards, single database sufficient
- **Issues**: 
  - I-001: /api/squire/systems endpoint broken (low priority)
  - I-002: No authentication system (high priority)
- **Dependencies**: PostgreSQL 16, GW IP, CDN dependencies

#### C. Design Decisions (`docs/design-decisions.md`)
**Purpose**: Record all architectural and design decisions with rationale

**Decisions Documented**:
- **DD-001**: **NO EMOJI ICONS IN UI** (ENFORCED)
  - All UI must use text labels, SVG icons, or icon fonts
  - Emoji strictly prohibited for professional appearance
  - Better accessibility and cross-platform rendering
  
- **DD-002**: Docker-based architecture
- **DD-003**: Alpine.js for frontend framework
- **DD-004**: Modular backend structure

#### D. Documentation Index (`docs/README.md`)
- Quick start guide
- Architecture overview
- Testing instructions
- Contributing guidelines
- Design principles reference

---

### 2. Frontend UX Fixes

Fixed `frontend/public/modules/squire/battleplan.js` to comply with design standards:

#### Changes Made:
1. **Removed ALL Emoji Icons** (DD-001 compliance)
   - ❌ Removed: ⚔️, 🏰, 🚀, 🛡️, 🎲, ⚠️, ✕, 📋, 🏆, 🎯, ⚡, 🖨️
   - ✅ Replaced with: Text labels, abbreviations (AoS, 40K, TOW), bullet points, proper symbols (×, !)

2. **Clarified Purpose and Context**
   - Changed title from "Battle Plan Randomizer" to "Battle Plan Reference"
   - Added prominent note explaining this is a practice/reference tool
   - Clarified that tournament battle plans are auto-generated during matchups
   - Updated "About This Tool" section to explain the difference

3. **Professional UI Improvements**
   - System buttons now show abbreviations (AoS, 40K, TOW) instead of emoji
   - Error display uses styled circle with exclamation mark instead of ⚠️ emoji
   - Section headers use uppercase tracking for emphasis instead of emoji prefixes
   - Bullet points use proper • character with bold styling

#### UX Messaging:
```
Battle Plan Reference
Browse and generate battle plans for practice and reference.

Note: This is a reference tool for practice. 
In tournaments, battle plans are automatically generated when both players submit their lists.

About This Tool:
- Practice & Reference: Use this tool to familiarize yourself with mission types
- Tournament Play: Battle plans are automatically generated when both players submit lists
- Fair Competition: Automated system ensures unbiased mission selection
```

---

### 3. Design Decision: No Emoji Rule

**Context**: Battle plan UI had emoji throughout (⚔️, 🎲, 🏰, etc.)

**Decision**: Strict no-emoji policy enforced (DD-001)

**Rationale**:
- Professional appearance for competitive gaming platform
- Better accessibility (screen readers)
- Consistent cross-platform rendering
- Serious tone appropriate for tournament management

**Implementation**:
- All existing emoji removed from battleplan.js
- Design decision documented in docs/design-decisions.md
- Future PRs will be rejected if they contain emoji

---

### 4. Corrected Feature Understanding

**Misunderstanding**: Battle Plan Randomizer was built as standalone tool for manual generation

**Actual Requirement**: Battle plans should be automatically revealed during tournament matchups

**User Stories Created**:
- **US-006**: System selection during list submission
- **US-007**: Automatic battle plan generation when lists are revealed  
- **US-008**: Matchup summary display with opponents, lists, and battle plan
- **US-009**: Current reference tool (what exists now)

**Next Steps**:
The integrated tournament feature (US-007, US-008) requires:
1. Herald tournament module implementation
2. List submission system with game system selection
3. Matchup pairing system
4. Automatic battle plan generation on list reveal
5. Matchup summary UI showing both lists + battle plan

---

## Files Modified

### Created:
- `docs/user-stories.md` - Complete user story register
- `docs/raid-log.md` - RAID tracking log
- `docs/design-decisions.md` - Architectural decision records
- `docs/README.md` - Documentation index

### Modified:
- `frontend/public/modules/squire/battleplan.js` - Removed emoji, clarified purpose

### Rebuilt:
- `squig-frontend` container - Applied UI changes
- `squig-nginx` container - Restarted to apply frontend changes

---

## Validation

Frontend changes deployed and accessible at:
- http://localhost/squire/battle-plan

**Verified**:
- ✅ All emoji removed from UI
- ✅ Professional text-based interface
- ✅ Clear messaging about tool purpose vs tournament integration
- ✅ Documentation structure in place
- ✅ Design decisions recorded
- ✅ User stories defined for future work

---

## Key Takeaways

1. **Always Define User Stories First**: New feature implementation must start with user story definition
2. **No Emoji Policy**: Strictly enforced across entire platform
3. **Documentation Required**: RAID log, design decisions, and user stories must be maintained
4. **Battle Plan Integration ≠ Reference Tool**: Current tool is for practice; tournament integration is separate feature requiring Herald module

---

## Next Steps for Battle Plan Integration

To implement the actual tournament feature (US-007, US-008):

1. Review and approve user stories US-006 through US-008
2. Design Herald tournament management module
3. Implement list submission with system selection
4. Create matchup pairing engine
5. Build matchup summary UI
6. Integrate Squire battle plan API with Herald matchups
7. Add automated battle plan generation trigger on list reveal

**Estimated Effort**: 3-4 sprints for complete tournament system
**Dependencies**: User authentication (US-020), database schema design
**Priority**: High (core platform functionality)

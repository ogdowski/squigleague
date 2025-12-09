# User Stories

## Purpose
This document contains all user stories for the SquigLeague platform, both implemented and planned.

## Story Format
- **Story ID**: Unique identifier (US-###)
- **Epic**: Which feature area this belongs to
- **Status**: Planned | In Progress | Implemented | Released
- **Priority**: Critical | High | Medium | Low
- **Story**: As a [role], I want [feature] so that [benefit]
- **Acceptance Criteria**: Specific testable conditions
- **Technical Notes**: Implementation details (optional)

---

## Epic: Herald - Tournament Administration

### US-001: Tournament Creation
**Status**: Planned  
**Priority**: Critical  
**Story**: As a tournament organizer, I want to create a new tournament with basic details (name, date, location, format) so that players can find and register for my event.

**Acceptance Criteria**:
- [ ] Can create tournament with name, date, location, game system
- [ ] Can set tournament format (single elimination, swiss, etc.)
- [ ] Can set player capacity
- [ ] Tournament gets unique URL/ID
- [ ] Can save as draft or publish

**Technical Notes**: Herald module, POST /api/herald/tournaments

---

### US-002: Player Registration
**Status**: Planned  
**Priority**: Critical  
**Story**: As a player, I want to register for a tournament so that I can participate in the event.

**Acceptance Criteria**:
- [ ] Can view tournament details before registering
- [ ] Can submit registration with player name and contact info
- [ ] Receive confirmation of registration
- [ ] Can view my registered tournaments
- [ ] Can withdraw from tournament before deadline

**Technical Notes**: Requires authentication system (US-020)

---

### US-003: List Submission
**Status**: Planned  
**Priority**: High  
**Story**: As a registered player, I want to submit my army list before the tournament deadline so that organizers can verify it meets requirements.

**Acceptance Criteria**:
- [ ] Can paste army list text
- [ ] Can upload list as file (PDF, TXT, etc.)
- [ ] System validates list format (basic checks)
- [ ] Can edit list before deadline
- [ ] Organizer can see all submitted lists
- [ ] List is locked after deadline

**Technical Notes**: Herald module, related to US-010

---

### US-004: Matchup Pairing
**Status**: Planned  
**Priority**: Critical  
**Story**: As a tournament organizer, I want the system to automatically generate round pairings based on tournament format so that I don't have to manually pair players.

**Acceptance Criteria**:
- [ ] System generates first round pairings (random or seeded)
- [ ] Subsequent rounds pair by record (swiss)
- [ ] Avoids repeat pairings when possible
- [ ] Handles odd number of players (bye rounds)
- [ ] Can manually adjust pairings if needed
- [ ] Can publish pairings to players

**Technical Notes**: Herald module, complex pairing algorithms

---

### US-005: Score Submission
**Status**: Planned  
**Priority**: High  
**Story**: As a player, I want to submit my game results after each round so that standings are updated correctly.

**Acceptance Criteria**:
- [ ] Can submit win/loss/draw result
- [ ] Can submit victory points scored
- [ ] Can submit secondary objectives scored
- [ ] Both players must confirm result (or organizer override)
- [ ] Standings update automatically after confirmation

**Technical Notes**: Herald module, POST /api/herald/results

---

## Epic: Squire - Matchup System

### US-006: Create Matchup with System Selection
**Status**: Implemented  
**Priority**: High  
**Story**: As a player, I want to create a matchup by selecting my game system so that I can share lists with my opponent.

**Acceptance Criteria**:
- [x] Can select game system (AoS, 40k, Old World)
- [x] System creates unique matchup ID/link
- [x] Can share link with opponent
- [x] Both players use same system

**Technical Notes**: 
- POST /api/squire/matchup/create
- Returns matchup_id and share link
- Frontend: /squire/matchup

---

### US-007: Submit Army List to Matchup
**Status**: Implemented  
**Priority**: High  
**Story**: As a player in a matchup, I want to paste my army list so that my opponent can see it when they also submit.

**Acceptance Criteria**:
- [x] Can paste army list text
- [x] List is hidden until both players submit
- [x] Can see when opponent has submitted (but not their list yet)
- [x] Cannot edit after submission

**Technical Notes**: 
- POST /api/squire/matchup/{id}/submit-list
- Stores player name + list text
- Polling every 5 seconds for updates

---

### US-008: View Matchup Summary with Battle Plan
**Status**: Implemented  
**Priority**: High  
**Story**: As a player, when both lists are submitted, I want to see the matchup summary with my opponent's list and a random battle plan for our system.

**Acceptance Criteria**:
- [x] Shows both player names
- [x] Shows both army lists side-by-side
- [x] Shows battle plan for selected system
- [x] Battle plan is randomized when both lists submitted
- [x] Can print matchup summary

**Technical Notes**: 
- GET /api/squire/matchup/{id}
- Auto-generates battle plan when both lists present
- Battle plan stored with matchup (no re-rolls)
- Frontend auto-updates via polling

---

### US-009: Battle Plan Reference
**Status**: Implemented  
**Priority**: Medium  
**Story**: As a player preparing for a tournament, I want to view all possible battle plans for my game system so that I can practice different scenarios.

**Acceptance Criteria**:
- [x] Can select game system (AoS, 40k, Old World)
- [x] Can generate random battle plan
- [x] Displays deployment map, primary objectives, and battle tactics
- [x] Can generate multiple plans to see variety
- [x] No account required (public tool)

**Technical Notes**: 
- Implemented in Squire module
- UI: /squire/battle-plan
- API: GET /api/squire/battle-plan/random?system={system}
- **NOTE**: This is a standalone tool, NOT the integrated tournament feature

---

### US-010: List Format Validation
**Status**: Planned  
**Priority**: Medium  
**Story**: As a tournament organizer, I want basic validation of submitted lists so that I can quickly identify formatting issues or missing information.

**Acceptance Criteria**:
- [ ] Checks for minimum required fields (points total, unit names)
- [ ] Warns if points seem incorrect for tournament limit
- [ ] Highlights if no system is selected
- [ ] Provides warning (not blocking) for unusual formatting
- [ ] Organizer can approve lists despite warnings

**Technical Notes**: Herald module, regex/text parsing

---

## Epic: User Management

### US-020: User Account Creation
**Status**: Planned  
**Priority**: Critical  
**Story**: As a new user, I want to create an account so that I can register for tournaments and track my gaming history.

**Acceptance Criteria**:
- [ ] Can register with email and password
- [ ] Email verification required
- [ ] Can set display name
- [ ] Can optionally link social accounts (Discord, Google)
- [ ] Account created before can be used

**Technical Notes**: Authentication system required (OAuth2 + JWT)

---

### US-021: User Login
**Status**: Planned  
**Priority**: Critical  
**Story**: As a returning user, I want to log in to my account so that I can access my tournaments and lists.

**Acceptance Criteria**:
- [ ] Can log in with email/password
- [ ] Can log in with social accounts
- [ ] Session persists across browser restarts
- [ ] Can log out
- [ ] "Remember me" option available

**Technical Notes**: JWT tokens, refresh tokens

---

### US-022: Password Reset
**Status**: Planned  
**Priority**: High  
**Story**: As a user who forgot my password, I want to reset it via email so that I can regain access to my account.

**Acceptance Criteria**:
- [ ] Can request password reset email
- [ ] Email contains secure reset link
- [ ] Link expires after 24 hours
- [ ] Can set new password
- [ ] Old password is invalidated

**Technical Notes**: Email service integration required

---

## Epic: Squire - Additional Player Tools

### US-030: Tournament Checklist
**Status**: Planned  
**Priority**: Low  
**Story**: As a player preparing for a tournament, I want a checklist of things to bring so that I don't forget important items.

**Acceptance Criteria**:
- [ ] Pre-populated checklist (army, dice, tape measure, etc.)
- [ ] Can add custom items
- [ ] Can check off items
- [ ] Persists across sessions
- [ ] Can reset checklist

**Technical Notes**: Squire module, simple localStorage

---

### US-031: Dice Roller
**Status**: Planned  
**Priority**: Low  
**Story**: As a player, I want a quick dice roller for casual games so that I don't need physical dice.

**Acceptance Criteria**:
- [ ] Can roll common dice types (D6, D3, etc.)
- [ ] Can roll multiple dice at once
- [ ] Shows roll history
- [ ] NOT for competitive play (disclaimer)

**Technical Notes**: Squire module, client-side only

---

## Story Template

```markdown
### US-###: [Story Title]
**Status**: Planned | In Progress | Implemented | Released  
**Priority**: Critical | High | Medium | Low  
**Story**: As a [role], I want [feature] so that [benefit].

**Acceptance Criteria**:
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Criteria 3

**Technical Notes**: [Optional implementation details]
```

---

## Story Status Definitions

- **Planned**: Story is defined but not yet started
- **In Progress**: Development work has begun
- **Implemented**: Code complete and tested, not yet deployed
- **Released**: Deployed to production and available to users

## Priority Definitions

- **Critical**: Core functionality, platform unusable without this
- **High**: Important feature, significantly impacts user experience
- **Medium**: Nice to have, improves user experience
- **Low**: Optional enhancement, minimal impact if delayed

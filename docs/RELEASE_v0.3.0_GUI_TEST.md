# Release v0.3.0 - Manual GUI Testing Checklist

## Test Environment
- Backend: http://localhost:8000 (API endpoints at `/api/squire/*`)
- Frontend: http://localhost:3000 (Single matchup interface)

## Pre-Flight Check
- [ ] Backend running: `$env:REQUIRE_DATABASE="false"; .\.venv\Scripts\python.exe -m uvicorn herald.main:app --reload --port 8000`
- [ ] Frontend running: `cd frontend/public; python -m http.server 3000`
- [ ] API tests passed: `.\scripts\test-release-v0.3.0.ps1` (8/8 tests)

---

## GUI Test Cases

### TEST 1: Page Load
**Steps:**
1. Open http://localhost:3000 in browser
2. Check page loads without errors
3. Open browser console (F12)

**Expected:**
- [ ] Page displays "SQUIG LEAGUE" header
- [ ] Navigation shows "List Exchange + Battle Plan Generator"
- [ ] Main content area shows matchup interface
- [ ] No JavaScript errors in console
- [ ] Footer shows copyright and version

**Notes:** _____________________________

---

### TEST 2: Create Matchup
**Steps:**
1. Select "Age of Sigmar" system
2. Click "Create Matchup" button

**Expected:**
- [ ] System button highlights when selected
- [ ] Matchup ID generated
- [ ] URL changes to `/matchup/{id}`
- [ ] Share URL displayed
- [ ] Player submission form appears

**Actual Matchup ID:** _____________________________

---

### TEST 3: Submit First Player List
**Steps:**
1. Enter player name: "Alice"
2. Paste army list:
   ```
   Stormcast Eternals - 2000pts
   
   Lord-Imperatant (General)
   3x Vindictors
   5x Liberators
   ```
3. Click "Submit My List"

**Expected:**
- [ ] Submission successful message
- [ ] "Waiting for opponent..." status
- [ ] Lists NOT visible yet
- [ ] No battle plan shown yet
- [ ] Polling starts (check network tab for repeated GET requests)

**Notes:** _____________________________

---

### TEST 4: Second Player Joins (Incognito/New Window)
**Steps:**
1. Copy matchup URL from step 2
2. Open in incognito window or new browser
3. Verify page loads with empty form
4. Enter player name: "Bob"
5. Paste army list:
   ```
   Lumineth Realm-lords - 2000pts
   
   Scinari Cathallar (General)
   10x Vanari Auralan Wardens
   5x Vanari Dawnriders
   ```
6. Click "Submit My List"

**Expected:**
- [ ] Matchup summary appears immediately
- [ ] Both player names displayed
- [ ] Both army lists visible
- [ ] Battle plan generated and displayed
- [ ] Battle plan includes:
  - [ ] Mission name
  - [ ] Deployment type
  - [ ] Objectives
  - [ ] Victory conditions
  - [ ] Special rules

**Battle Plan Name:** _____________________________

---

### TEST 5: First Player View Updates
**Steps:**
1. Return to first browser window (Alice)
2. Wait for automatic update (polling)

**Expected:**
- [ ] Page updates automatically (within 5-10 seconds)
- [ ] Matchup summary now visible
- [ ] Both lists displayed
- [ ] Same battle plan as Player 2 sees

**Notes:** _____________________________

---

### TEST 6: API Endpoints via Browser Console
**Steps:**
1. Open browser console on http://localhost:3000
2. Run:
   ```javascript
   fetch('http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar')
     .then(r => r.json())
     .then(data => console.log('Battle Plan:', data.name, '-', data.deployment))
   ```

**Expected:**
- [ ] CORS error appears (expected - different port)
- [ ] OR battle plan data returned if CORS configured

**Note:** This confirms frontend/backend are on different ports. Production uses nginx to proxy.

---

## Known Limitations (Expected Behavior)

- [ ] Frontend at port 3000, backend at 8000 = CORS issues with direct API calls from browser
- [ ] Matchups stored in memory - restart clears all data
- [ ] No authentication - anyone with URL can view matchup
- [ ] Only AoS supported (40k and Old World return placeholder data)
- [ ] Database errors in backend logs are normal (Herald module disabled)

---

## Test Results Summary

**Date:** _____________________________
**Tester:** _____________________________

**Overall Status:** [ ] PASS / [ ] FAIL

**Issues Found:**
1. _____________________________
2. _____________________________
3. _____________________________

**Blocker Issues (prevent release):**
- _____________________________

**Minor Issues (can be fixed later):**
- _____________________________

---

## Sign-Off

- [ ] All core functionality works
- [ ] No critical bugs found
- [ ] GUI matches expected design
- [ ] Ready for release tag

**Approved By:** _____________________________
**Date:** _____________________________

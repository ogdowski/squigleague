# Battle Plan Polish & Image Refinement Plan

**Date Created**: 2026-01-16  
**Branch**: feature/matplotlib-battleplan-diagrams  
**Status**: Ready for polishing phase

---

## Current State Summary

### ✅ What Already Exists

**12 Battle Plans Implemented:**
1. Passing Seasons
2. Paths of the Fey
3. Roiling Roots
4. Cyclic Shifts
5. Surge of Slaughter
6. Linked Ley Lines
7. Noxious Nexus
8. The Liferoots
9. Bountiful Equinox
10. Lifecycle
11. Creeping Corruption
12. Grasp of Thorns

**Assets Available:**
- `assets/battle-plans/` - 12 PNG images from Wahapedia (reference)
- `assets/battle-plans-matplotlib/` - 12 matplotlib-generated diagrams
- Multiple extraction scripts in `scripts/`
- Generated IP-neutral tactical diagrams

**Code/Data:**
- `scripts/generate_matplotlib_battleplans.py` - Main diagram generator (352 lines)
- 25+ extraction/analysis scripts for image processing
- Extracted objectives JSON data
- Template matching results

---

## Baseline (Not To Be Modified)

**The following are DEFINITE and LOCKED:**

1. **12 Battle Plan Names** - From General's Handbook 2025-2026
2. **Battle Plan Data** - In backend code (deployment zones, objectives, scoring)
3. **Number of Objectives** - Per battle plan (ranging from 2-6 objectives)
4. **Game Rules** - Scoring mechanics, underdog abilities, special rules

**These are REFERENCE ONLY** - Do not modify battle plan definitions.

---

## What Needs Polishing

### 1. Image Quality & Consistency

**Current Issues to Address:**
- [ ] Verify all 12 matplotlib diagrams match official layouts
- [ ] Ensure consistent visual style across all diagrams
- [ ] Check deployment zone accuracy
- [ ] Verify objective marker positioning
- [ ] Confirm all diagrams use same scale/grid

**Quality Standards:**
- High DPI (150+ recommended)
- Clear objective numbering
- Readable deployment zone labels
- Consistent color scheme
- Professional appearance

### 2. Image Metadata & Organization

**File Naming Convention:**
- Format: `aos-{mission-slug}-matplotlib.png`
- Example: `aos-passing-seasons-matplotlib.png`
- All lowercase with hyphens

**Required Documentation:**
- [ ] Each image needs source attribution
- [ ] Coordinate extraction methodology documented
- [ ] Any manual adjustments noted

### 3. Verification Against Official Sources

**Checklist per Battle Plan:**
- [ ] Deployment zones match GH 2025-26 descriptions
- [ ] Objective count correct
- [ ] Objective positioning matches Wahapedia reference
- [ ] Special terrain features included (if applicable)
- [ ] Grid overlay accurate (60" x 44" battlefield)

### 4. Code Quality & Documentation

**Scripts to Review:**
- [ ] `generate_matplotlib_battleplans.py` - Main generator
- [ ] Extraction scripts organization
- [ ] Remove unused/debug scripts
- [ ] Add docstrings to all functions
- [ ] Create usage README in scripts/

**Data Files:**
- [ ] Clean up intermediate JSON files
- [ ] Keep only final extraction results
- [ ] Document JSON schema

### 5. Integration with Backend

**Ensure Images Are Accessible:**
- [ ] Images served via static file endpoint
- [ ] URLs in battle_plans.py data correct
- [ ] Test image loading in frontend
- [ ] Verify CORS headers if needed

---

## Polishing Tasks (Ordered by Priority)

### Phase 1: Verification (2-3 hours)
1. Open each matplotlib diagram side-by-side with Wahapedia reference
2. Create verification checklist spreadsheet
3. Note any discrepancies in objective positions
4. Document any visual style inconsistencies

### Phase 2: Corrections (3-4 hours)
1. Fix any objective positioning errors
2. Standardize visual style (colors, fonts, sizes)
3. Ensure deployment zones are identical across all diagrams
4. Regenerate any diagrams with issues

### Phase 3: Documentation (1-2 hours)
1. Complete `BATTLE_PLAN_IMAGE_SOURCES.md`
2. Add README to `assets/battle-plans-matplotlib/`
3. Document extraction methodology
4. Create visual comparison gallery (HTML)

### Phase 4: Cleanup (1 hour)
1. Remove debug images
2. Organize scripts into logical folders
3. Delete unused extraction attempts
4. Keep only final working scripts

### Phase 5: Testing (1 hour)
1. Verify images load in backend
2. Test frontend display
3. Check mobile rendering
4. Validate accessibility (alt text, etc.)

---

## File Locations Reference

```
assets/
├── battle-plans/                           # Wahapedia references (DO NOT MODIFY)
│   ├── aos-passing-seasons.png
│   ├── aos-paths-of-the-fey.png
│   └── ... (12 total)
│
└── battle-plans-matplotlib/                # Generated diagrams (POLISH THESE)
    ├── aos-passing-seasons-matplotlib.png
    ├── aos-paths-of-the-fey-matplotlib.png
    └── ... (12 total + extraction artifacts)

scripts/
├── generate_matplotlib_battleplans.py      # Main diagram generator
├── extract_*.py                            # Extraction scripts
├── analyze_*.py                            # Analysis scripts
└── ... (25+ scripts total)

docs/
├── BATTLE_PLAN_IMAGE_SOURCES.md           # EMPTY - needs content
├── BATTLE_PLANS_DATA_ANALYSIS.md          # Extraction methodology
└── BATTLE_PLAN_POLISH_PLAN.md             # This file
```

---

## Success Criteria

**Before considering this task complete:**

✅ All 12 diagrams verified against official sources  
✅ Consistent visual style across all diagrams  
✅ High-quality PNG files (150+ DPI)  
✅ Documentation complete (sources, methodology)  
✅ Images accessible from backend API  
✅ Frontend displays images correctly  
✅ Scripts organized and documented  
✅ Cleanup complete (no debug artifacts)  
✅ Verification gallery created for QA  

---

## Notes

- **IP Compliance**: Matplotlib diagrams are IP-neutral (no GW artwork/logos)
- **Source Attribution**: Wahapedia references for coordinate extraction
- **Extensibility**: System designed for future 40k/Old World diagrams
- **Automation**: All diagrams generated from code (reproducible)

---

## Next Steps

1. Review this plan with user to confirm scope
2. Create verification checklist spreadsheet
3. Begin Phase 1: Verification
4. Report findings before making corrections
5. Proceed through remaining phases systematically


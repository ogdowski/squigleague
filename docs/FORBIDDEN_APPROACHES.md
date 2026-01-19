# FORBIDDEN APPROACHES

This document tracks approaches that have been attempted and MUST NOT be repeated.

---

## [FORBIDDEN-001] Matplotlib Diagram Generation from objectives_corrected.json

**Date**: 2026-01-19  
**Severity**: CRITICAL - Complete waste of time

**What Was Attempted**:
- Reading coordinate data from `assets/battle-plans-matplotlib/objectives_corrected.json`
- Generating matplotlib diagrams with deployment zones and objective markers
- Creating battle plan images from scratch using matplotlib

**Why This Is Wrong**:
- Wrong data source: `objectives_corrected.json` contains EXTRACTED coordinates from existing images, not source data
- Wrong process: The matplotlib images ALREADY EXIST in the repository
- Wrong output: Generated new matplotlib diagrams instead of enhancing existing images
- Complete misunderstanding of the task

**Files Created (ALL DELETED)**:
- `scripts/generate_battle_plans.py` - DELETED
- `scripts/generate_enhanced_battleplans.py` - DELETED
- 12 matplotlib PNG files in `frontend/public/assets/battle-plans-enhanced/` - DELETED
- 12 matplotlib PNG files regenerated in `assets/battle-plans-matplotlib/` - RESTORED from git

**The Actual Task** (NOT YET UNDERSTOOD):
- The matplotlib images already exist and are committed in git
- The task involves some kind of visual enhancement or backdrop modification
- The user has been trying to explain this for hours
- Agent keeps creating wrong scripts instead of understanding requirements

**Prevention**:
- [ ] DO NOT generate matplotlib diagrams from objectives_corrected.json
- [ ] DO NOT create scripts that read coordinate data and draw diagrams
- [ ] DO NOT assume you understand the task without reading ALL documentation
- [ ] DO NOT create new files without understanding what already exists
- [ ] LISTEN to the user when they say "WRONG"

**Related Issues**: Complete failure to understand task despite multiple explanations

---

## Instructions for Future Sessions

If you are asked to work on battle plan images:

1. STOP
2. Read this document
3. Ask the user to explain EXACTLY what the source files are
4. Ask the user to explain EXACTLY what the output should be
5. Ask the user to show an example of what they want
6. DO NOT assume anything
7. DO NOT create scripts based on assumptions

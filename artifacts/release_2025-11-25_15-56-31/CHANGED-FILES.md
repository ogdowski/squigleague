# Changed Files for PR

## Backend
- squire/matchup.py (NEW) - Matchup data models and business logic
- squire/routes.py (MODIFIED) - Added matchup API endpoints
- tests/integration/squire/test_matchup.py (NEW) - Comprehensive test suite

## Frontend  
- frontend/public/modules/squire/matchup.js (NEW) - Matchup UI component
- frontend/public/modules/squire/battleplan-reference.js (NEW) - Battle plan reference page
- frontend/public/modules/squire/battleplan.js (MODIFIED) - Removed emoji
- frontend/public/modules/herald/home.js (MODIFIED) - Removed emoji
- frontend/public/modules/herald/waiting.js (MODIFIED) - Removed emoji
- frontend/public/modules/herald/reveal.js (MODIFIED) - Removed emoji
- frontend/public/src/main.js (MODIFIED) - Added routing
- frontend/public/index.html (MODIFIED) - Added navigation

## Configuration
- nginx/nginx.conf (MODIFIED) - Fixed syntax errors, removed 'just', fixed admin IP

## Scripts
- scripts/run-tests.ps1 (NEW) - Automated test runner
- scripts/rebuild-all.ps1 (NEW) - Container rebuild script
- scripts/export-battleplans.ps1 (NEW) - Battle plan export script
- scripts/prepare-release.ps1 (NEW) - Release preparation orchestration
- scripts/test-api.ps1 (NEW) - API integration tests
- scripts/test-matchup-flow.ps1 (NEW) - End-to-end flow test
- scripts/MATCHUP-FLOW.md (NEW) - User flow documentation

## Documentation
- PR-SUMMARY.md (NEW) - Pull request summary

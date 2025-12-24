# Playwright Technical Debt - Commandment 26 Violation

**Status:** VIOLATION - Requires Remediation  
**Commandment:** 26 (Sacred Testing Tools)  
**Severity:** HIGH  
**Created:** December 24, 2025

---

## Violation Summary

The workspace contains **Playwright** E2E testing framework, which violates **Commandment 26**:

> "Backend testing MUST use pytest exclusively. Frontend/E2E testing MUST use Selenium WebDriver exclusively. Jest, Vite testing, Playwright, Cypress, Puppeteer are STRICTLY FORBIDDEN."

## Current State

**Playwright Files Detected:**
- `e2e/playwright.config.js` - Playwright configuration
- `e2e/package.json` - Contains Playwright dependencies
- `e2e/tests/*.spec.js` - Playwright test files

**Documentation References:**
- `docs/TESTING_DEPLOYMENT_STRATEGY.md` - References Playwright
- `scripts/pre-deployment-check.ps1` - Checks for Playwright tests
- `tests/integration/backend/README.md` - Mentions Playwright

## Required Remediation

### Phase 1: Immediate (Pre-Deployment)
- [x] Document violation in this file
- [x] Update `.github/copilot-instructions.md` with strengthened Selenium requirement
- [ ] Add note to deployment checklist about E2E non-compliance
- [ ] Freeze new Playwright test development

### Phase 2: Migration (2 Weeks)
- [ ] Install Selenium WebDriver: `pip install selenium`
- [ ] Create Python-based E2E test structure
- [ ] Rewrite `login-flow.spec.js` → `test_login_flow.py` (Selenium)
- [ ] Rewrite `user-profile.spec.js` → `test_user_profile.py` (Selenium)
- [ ] Configure WebDriver (ChromeDriver, geckodriver)
- [ ] Update CI/CD to run Selenium tests

### Phase 3: Cleanup (After Migration)
- [ ] Remove `e2e/playwright.config.js`
- [ ] Remove Playwright from `e2e/package.json`
- [ ] Remove all `.spec.js` test files
- [ ] Update all documentation references
- [ ] Add Selenium validation to `pre-deployment-check.ps1`

## Proposed Selenium Structure

```
e2e/
├── requirements.txt          # selenium, pytest-selenium
├── conftest.py              # Selenium fixtures
├── tests/
│   ├── test_login_flow.py   # Replaces login-flow.spec.js
│   └── test_user_profile.py # Replaces user-profile.spec.js
└── pages/                   # Page Object Models
    ├── login_page.py
    └── profile_page.py
```

## Example Selenium Test

```python
# e2e/tests/test_login_flow.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_user_can_login(driver, base_url):
    """Test successful user login flow."""
    driver.get(f"{base_url}/login")
    
    # Enter credentials
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    
    username_input.send_keys("test_user")
    password_input.send_keys("test_password")
    
    # Submit form
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    
    # Verify redirect to dashboard
    WebDriverWait(driver, 10).until(
        EC.url_contains("/matchup")
    )
    
    assert "/matchup" in driver.current_url
```

## Migration Timeline

| Week | Tasks | Deliverable |
|------|-------|-------------|
| 1 | Install Selenium, create structure, rewrite login test | `test_login_flow.py` passing |
| 2 | Rewrite profile test, update CI/CD, remove Playwright | Selenium fully integrated |

## Deployment Decision

**Option 1: Deploy with Exception**
- Document this violation as known technical debt
- Deploy with unit tests (100% coverage)
- Complete Selenium migration post-deployment

**Option 2: Hold Deployment**
- Block deployment until Selenium migration complete
- Requires 2-week timeline
- Risk: Delays features and fixes

**Recommended:** Option 1 with 2-week migration commitment

## Compliance Checklist

- [x] Violation documented
- [x] Copilot instructions updated
- [ ] Migration plan approved
- [ ] Selenium installation complete
- [ ] All tests migrated
- [ ] Playwright removed
- [ ] Documentation updated
- [ ] CI/CD updated
- [ ] Compliance verified

## Notes

- **Backend testing:** ✅ COMPLIANT (pytest exclusive)
- **Frontend E2E testing:** ❌ NON-COMPLIANT (Playwright instead of Selenium)
- **Impact:** E2E tests are optional; unit tests provide production readiness
- **Urgency:** HIGH (governance violation) but not blocking (tests optional)

---

**Next Action:** Approve migration plan or request deployment exception.

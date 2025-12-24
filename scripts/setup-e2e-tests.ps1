# E2E Testing Setup (Selenium)
# Purpose: Ensure dependencies are installed and point to the pytest-based Selenium suite.

Write-Host "=== Selenium E2E Setup ===" -ForegroundColor Cyan

# Verify Python venv activation
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not detected in PATH. Activate your venv first: .\.venv\Scripts\Activate.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "`n[1/3] Installing test dependencies (includes selenium, webdriver-manager)..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

Write-Host "`n[2/3] Verifying selenium import..." -ForegroundColor Yellow
try {
    python - <<'PY'
import selenium  # noqa: F401
import webdriver_manager  # noqa: F401
print("selenium + webdriver-manager available")
PY
} catch {
    Write-Host "Selenium not available. See errors above." -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/3] How to run E2E:" -ForegroundColor Yellow
Write-Host "  1) Start backend + frontend (just dev or docker-compose)" -ForegroundColor White
Write-Host "  2) Set TEST_BASE_URL (e.g., http://localhost:8000)" -ForegroundColor White
Write-Host "  3) Run: pytest tests/e2e/selenium --run-e2e --headed" -ForegroundColor White

Write-Host "`n=== Selenium setup complete ===" -ForegroundColor Green

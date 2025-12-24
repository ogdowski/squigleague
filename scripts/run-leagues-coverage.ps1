# Run leagues tests with 100% coverage requirement
# This script runs all leagues module tests with coverage scoped to app.leagues

$ErrorActionPreference = "Stop"

# Set environment variables
$env:DATABASE_URL = "sqlite:///:memory:"
$env:PYTHONPATH = "C:/repos/SquigLeague/squigleague/backend"

# Change to repo root
Set-Location "C:/repos/SquigLeague"

Write-Host "Running leagues tests with 100% coverage target..." -ForegroundColor Cyan
Write-Host ""

# Run pytest with coverage
& "C:/repos/SquigLeague/.venv/Scripts/python.exe" -m pytest `
    squigleague/backend/tests/test_leagues_scoring.py `
    squigleague/backend/tests/test_leagues_service.py `
    squigleague/backend/tests/test_leagues_routes.py `
    squigleague/backend/tests/test_leagues_models.py `
    -o addopts="" `
    --cov=app.leagues `
    --cov-branch `
    --cov-report=term-missing `
    --cov-report=html `
    --cov-fail-under=100 `
    -v

$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: All leagues tests passed with 100% coverage!" -ForegroundColor Green
    Write-Host "HTML report: squigleague/htmlcov/index.html" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "FAILED: Coverage is below 100% or tests failed." -ForegroundColor Red
    Write-Host "Check the output above for missing lines." -ForegroundColor Yellow
}

exit $exitCode

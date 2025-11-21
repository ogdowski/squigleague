# Run local tests to identify failures
Write-Host "`n=== RUNNING LOCAL TESTS ===`n" -ForegroundColor Cyan

$python = "E:/repos/suigleague/.venv/Scripts/python.exe"

# Run pytest with verbose output
& $python -m pytest tests/integration/squire/ -v --tb=short

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ TESTS FAILED" -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n✅ TESTS PASSED" -ForegroundColor Green
    exit 0
}

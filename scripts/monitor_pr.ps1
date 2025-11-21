# Monitor CI without blocking - just check current status
.\scripts\check_ci_status.ps1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ PR CHECKS PASSED - Ready to merge!" -ForegroundColor Green
} elseif ($LASTEXITCODE -eq 2) {
    Write-Host "`nℹ️ Run this script again to check status" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Checks failed - see errors above" -ForegroundColor Red
}

# Browser Cache Clear Instructions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BROWSER CACHE ISSUE DETECTED" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The server is correctly returning 12 battle plans," -ForegroundColor Green
Write-Host "but your browser is using cached JavaScript." -ForegroundColor Yellow
Write-Host ""
Write-Host "TO FIX - Choose ONE option:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1 (Quick): Hard Refresh" -ForegroundColor White
Write-Host "  1. Go to http://localhost/squire/battleplan-reference" -ForegroundColor Gray
Write-Host "  2. Press Ctrl+F5 (or Ctrl+Shift+R on some browsers)" -ForegroundColor Gray
Write-Host "  3. Select Age of Sigmar" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2 (Thorough): Clear Cache" -ForegroundColor White
Write-Host "  1. Press Ctrl+Shift+Delete" -ForegroundColor Gray
Write-Host "  2. Select 'Cached images and files'" -ForegroundColor Gray
Write-Host "  3. Click Clear" -ForegroundColor Gray
Write-Host "  4. Go to http://localhost/squire/battleplan-reference" -ForegroundColor Gray
Write-Host "  5. Select Age of Sigmar" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 3 (Developer): Open DevTools" -ForegroundColor White
Write-Host "  1. Press F12 to open Developer Tools" -ForegroundColor Gray
Write-Host "  2. Right-click the refresh button" -ForegroundColor Gray
Write-Host "  3. Select 'Empty Cache and Hard Reload'" -ForegroundColor Gray
Write-Host ""
Write-Host "After clearing cache, you should see:" -ForegroundColor Cyan
Write-Host "  '12 Battle Plans Available' for Age of Sigmar" -ForegroundColor Green
Write-Host ""

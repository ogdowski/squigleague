# Monitor CI Status for Latest Run
# Non-blocking script to check CI status

Write-Host "=== MONITORING CI RUN ===" -ForegroundColor Cyan
Write-Host ""

$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Host "ERROR: GITHUB_TOKEN environment variable not set" -ForegroundColor Red
    Write-Host "Set it with: `$env:GITHUB_TOKEN = 'your_token'" -ForegroundColor Yellow
    exit 1
}

$headers = @{
    Authorization = "token $token"
    Accept = "application/vnd.github.v3+json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/ogdowski/squigleague/actions/runs?branch=feature/battle-plan-randomizer&per_page=1" -Headers $headers
    
    $run = $response.workflow_runs[0]
    
    Write-Host "Latest CI Run:" -ForegroundColor Yellow
    Write-Host "  Run ID: $($run.id)"
    Write-Host "  Commit: $($run.head_sha.Substring(0,7))"
    Write-Host "  Status: $($run.status)" -ForegroundColor $(if ($run.status -eq 'completed') { 'White' } else { 'Yellow' })
    Write-Host "  Conclusion: $($run.conclusion)" -ForegroundColor $(if ($run.conclusion -eq 'success') { 'Green' } elseif ($run.conclusion -eq 'failure') { 'Red' } else { 'Yellow' })
    Write-Host "  URL: $($run.html_url)"
    Write-Host ""
    
    if ($run.status -ne 'completed') {
        Write-Host "CI is still running. Check back later." -ForegroundColor Yellow
    } elseif ($run.conclusion -eq 'success') {
        Write-Host "CI PASSED!" -ForegroundColor Green
    } else {
        Write-Host "CI FAILED" -ForegroundColor Red
        Write-Host ""
        Write-Host "Fetch logs with:" -ForegroundColor Yellow
        Write-Host "  .\scripts\fetch_ci_logs.ps1 -RunId $($run.id)"
    }
} catch {
    Write-Host "ERROR: Failed to fetch CI status" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

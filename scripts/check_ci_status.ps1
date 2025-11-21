# Check CI status for feature branch
$branch = "feature/battle-plan-randomizer"
$repo = "ogdowski/squigleague"

Write-Host "`n=== CHECKING CI STATUS FOR $branch ===`n" -ForegroundColor Cyan

# Get latest run via API
$uri = "https://api.github.com/repos/$repo/actions/runs?branch=$branch&per_page=1"
$response = Invoke-RestMethod -Uri $uri -Method Get
$runs = $response.workflow_runs

if ($runs.Count -eq 0) {
    Write-Host "No CI runs found for branch $branch" -ForegroundColor Red
    exit 1
}

$run = $runs[0]
Write-Host "Run ID: $($run.id)"
Write-Host "Status: $($run.status)"
Write-Host "Conclusion: $($run.conclusion)"
Write-Host ""

if ($run.status -eq "completed") {
    if ($run.conclusion -eq "success") {
        Write-Host "✅ ALL CHECKS PASSED" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ CHECKS FAILED`n" -ForegroundColor Red
        
        # Get jobs
        $jobsUri = "https://api.github.com/repos/$repo/actions/runs/$($run.id)/jobs"
        $jobsResponse = Invoke-RestMethod -Uri $jobsUri -Method Get
        
        foreach ($job in $jobsResponse.jobs) {
            if ($job.conclusion -eq "failure") {
                Write-Host "FAILED JOB: $($job.name)" -ForegroundColor Red
                Write-Host "URL: $($job.html_url)" -ForegroundColor Yellow
            }
        }
        
        exit 1
    }
} else {
    Write-Host "⏳ CI still running..." -ForegroundColor Yellow
    exit 2
}

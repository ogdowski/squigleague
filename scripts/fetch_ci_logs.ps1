# Fetch CI job logs and extract errors
param(
    [string]$RunId = "19568514876"
)

$repo = "ogdowski/squigleague"
$token = $env:GITHUB_TOKEN

if (-not $token) {
    Write-Host "ERROR: GITHUB_TOKEN environment variable not set" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== FETCHING CI LOGS FOR RUN $RunId ===`n" -ForegroundColor Cyan

# Get jobs for this run
$jobsUri = "https://api.github.com/repos/$repo/actions/runs/$RunId/jobs"
$headers = @{
    "Authorization" = "Bearer $token"
    "Accept" = "application/vnd.github+json"
}

$jobsResponse = Invoke-RestMethod -Uri $jobsUri -Headers $headers -Method Get

foreach ($job in $jobsResponse.jobs) {
    if ($job.conclusion -eq "failure") {
        Write-Host "`n━━━ FAILED JOB: $($job.name) ━━━" -ForegroundColor Red
        
        # Get log URL
        $logUri = "https://api.github.com/repos/$repo/actions/jobs/$($job.id)/logs"
        
        try {
            $logs = Invoke-RestMethod -Uri $logUri -Headers $headers -Method Get
            
            # Extract test failure section
            $lines = $logs -split "`n"
            $startIndex = -1
            $endIndex = -1
            
            for ($i = 0; $i -lt $lines.Count; $i++) {
                if ($lines[$i] -match "Run tests with coverage|pytest|FAILED|ERROR") {
                    if ($startIndex -eq -1) { $startIndex = [Math]::Max(0, $i - 5) }
                    $endIndex = [Math]::Min($lines.Count - 1, $i + 10)
                }
            }
            
            if ($startIndex -ge 0) {
                $errorLines = $lines[$startIndex..$endIndex]
            } else {
                $errorLines = $lines | Where-Object { $_ -match "ERROR|FAILED|error" } | Select-Object -First 50
            }
            
            if ($errorLines) {
                Write-Host "`nERROR LINES:" -ForegroundColor Yellow
                $errorLines | ForEach-Object { Write-Host $_ }
            }
        } catch {
            Write-Host "Could not fetch logs: $_" -ForegroundColor Red
        }
    }
}

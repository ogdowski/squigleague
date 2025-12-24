<#
Generate SHA256 checksums for approved scripts and write `allowed-scripts.json`.

Usage:
  .\scripts\generate-checksums.ps1 -Scripts manual-test-auth.ps1,setup-database.ps1

This will compute the SHA256 for each provided script and update `scripts/allowed-scripts.json`.
#>

param(
    [Parameter(Mandatory=$false)]
    [string[]]$Scripts = @()
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$allowedFile = Join-Path $scriptDir "allowed-scripts.json"

if (-not (Test-Path $allowedFile)) {
    $template = @{ version = "1"; generated = ""; scripts = @{} } | ConvertTo-Json -Depth 5
    $template | Out-File -FilePath $allowedFile -Encoding utf8
}

$allowed = Get-Content $allowedFile -Raw | ConvertFrom-Json

if ($Scripts.Count -eq 0) {
    # default to all ps1 files in scripts dir
    $Scripts = Get-ChildItem -Path $scriptDir -Filter "*.ps1" | Where-Object { $_.Name -ne 'generate-checksums.ps1' -and $_.Name -ne 'runner.ps1' } | Select-Object -ExpandProperty Name
}

$scriptsHash = @{}
if ($allowed.scripts -is [PSCustomObject]) {
    # Convert existing PSCustomObject to hashtable
    $allowed.scripts.PSObject.Properties | ForEach-Object { $scriptsHash[$_.Name] = $_.Value }
}

foreach ($s in $Scripts) {
    $path = Join-Path $scriptDir $s
    if (-not (Test-Path $path)) {
        Write-Warning "Script not found: $path - skipping"
        continue
    }
    $hash = (Get-FileHash -Path $path -Algorithm SHA256).Hash.ToLower()
    $scriptsHash[$s] = $hash
    Write-Host "$s -> $hash"
}

$allowed.scripts = $scriptsHash

$allowed.generated = (Get-Date).ToString("s")
$allowed | ConvertTo-Json -Depth 5 | Out-File -FilePath $allowedFile -Encoding utf8
Write-Host "Updated $allowedFile"
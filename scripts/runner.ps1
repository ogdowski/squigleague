<#
scripts/runner.ps1

Safe runner for activity scripts. Enforces a whitelist and SHA256 checksum verification
before executing any script in the `scripts/` folder.

Usage:
  .\scripts\runner.ps1 -Script manual-test-auth.ps1 [-WhatIf]

Behavior:
  - Reads `scripts/allowed-scripts.json` to get approved script names and their SHA256.
  - If the script is not in the whitelist, it refuses to run.
  - If the checksum doesn't match, it refuses to run.
  - Runs the script in a separate PowerShell process and logs output to `scripts/runner.log`.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Script,

    [switch]$WhatIf
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$allowedFile = Join-Path $scriptDir "allowed-scripts.json"
$logFile = Join-Path $scriptDir "runner.log"

function Log($msg) {
    $time = (Get-Date).ToString("s")
    "$time - $msg" | Out-File -FilePath $logFile -Append -Encoding utf8
}

if (-not (Test-Path $allowedFile)) {
    Write-Error "Allowed scripts file not found: $allowedFile. Please run generate-checksums.ps1 to create it."
    exit 2
}

$allowed = Get-Content $allowedFile -Raw | ConvertFrom-Json

# Normalize script name
$scriptName = [IO.Path]::GetFileName($Script)
$scriptPath = Join-Path $scriptDir $scriptName

# Convert scripts to hashtable if needed
$scriptsHash = @{}
if ($allowed.scripts -is [PSCustomObject]) {
    $allowed.scripts.PSObject.Properties | ForEach-Object { $scriptsHash[$_.Name] = $_.Value }
} else {
    $scriptsHash = $allowed.scripts
}

if (-not $scriptsHash.ContainsKey($scriptName)) {
    Write-Error "Script '$scriptName' is not in allowed-scripts.json whitelist. Aborting."
    Log "REFUSED: $scriptName not in whitelist"
    exit 3
}

if (-not (Test-Path $scriptPath)) {
    Write-Error "Script file not found: $scriptPath"
    Log "REFUSED: $scriptPath not found"
    exit 4
}

# Compute SHA256
$hash = (Get-FileHash -Path $scriptPath -Algorithm SHA256).Hash.ToLower()
$expected = ($scriptsHash[$scriptName]).ToLower()

if ($hash -ne $expected) {
    Write-Error "Checksum mismatch for $scriptName. Expected: $expected; Actual: $hash. Aborting."
    Log "REFUSED: $scriptName checksum mismatch. expected=$expected actual=$hash"
    exit 5
}

Write-Host "Running allowed script: $scriptName" -ForegroundColor Green
Log "EXECUTE: $scriptName (checksum verified)"

if ($WhatIf) {
    Write-Host "WhatIf: would execute $scriptPath" -ForegroundColor Yellow
    Log "WHATIF: $scriptName"
    exit 0
}

# Execute the script in a new PowerShell process for isolation
$pwsh = $PSHOME + '\powershell.exe'
$startInfo = @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', "$scriptPath"
)

$proc = Start-Process -FilePath $pwsh -ArgumentList $startInfo -NoNewWindow -PassThru -Wait -RedirectStandardOutput (Join-Path $scriptDir "$scriptName.output.log") -RedirectStandardError (Join-Path $scriptDir "$scriptName.error.log")

if ($proc.ExitCode -eq 0) {
    Write-Host "Script $scriptName completed successfully." -ForegroundColor Green
    Log "SUCCESS: $scriptName exit=0"
    exit 0
} else {
    Write-Error "Script $scriptName failed with exit code $($proc.ExitCode). See ${scriptName}.error.log"
    Log "FAIL: $scriptName exit=$($proc.ExitCode)"
    exit $proc.ExitCode
}

# Activity: Generate matplotlib battle plan diagrams matching actual AOS_BATTLE_PLANS data
# Validates against Wahapedia originals to ensure correctness

$ErrorActionPreference = "Stop"

Write-Host "=" * 80
Write-Host "Generating Matplotlib Battle Plan Diagrams"
Write-Host "=" * 80

# Step 1: Verify we have the source images to reference
Write-Host "`nStep 1: Validating Wahapedia source images..."
$wahapediaImages = Get-ChildItem assets\battle-plans\*.png
if ($wahapediaImages.Count -ne 12) {
    Write-Error "Expected 12 Wahapedia images, found $($wahapediaImages.Count)"
}

$expectedFiles = @(
    'aos-passing-seasons.png',
    'aos-paths-of-the-fey.png',
    'aos-roiling-roots.png',
    'aos-cyclic-shifts.png',
    'aos-surge-of-slaughter.png',
    'aos-linked-ley-lines.png',
    'aos-noxious-nexus.png',
    'aos-the-liferoots.png',
    'aos-bountiful-equinox.png',
    'aos-lifecycle.png',
    'aos-creeping-corruption.png',
    'aos-grasp-of-thorns.png'
)

foreach ($file in $expectedFiles) {
    if (-not (Test-Path "assets\battle-plans\$file")) {
        Write-Error "Missing Wahapedia image: $file"
    }
}
Write-Host "✓ All 12 Wahapedia images present"

# Step 2: Clear old matplotlib images
Write-Host "`nStep 2: Clearing old matplotlib images..."
if (Test-Path assets\battle-plans-matplotlib) {
    Remove-Item assets\battle-plans-matplotlib\*.png -ErrorAction SilentlyContinue
    Write-Host "✓ Cleared old images"
} else {
    New-Item -ItemType Directory -Path assets\battle-plans-matplotlib -Force | Out-Null
    Write-Host "✓ Created matplotlib directory"
}

# Step 3: Generate matplotlib images
Write-Host "`nStep 3: Generating matplotlib diagrams..."
Write-Host "Running: .\.venv\Scripts\python.exe .\scripts\generate_matplotlib_battleplans.py"

.\.venv\Scripts\python.exe .\scripts\generate_matplotlib_battleplans.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "Matplotlib generation failed with exit code $LASTEXITCODE"
}

# Step 4: Validate output
Write-Host "`nStep 4: Validating generated images..."
$matplotlibImages = Get-ChildItem assets\battle-plans-matplotlib\*.png

if ($matplotlibImages.Count -ne 12) {
    Write-Error "Expected 12 matplotlib images, generated $($matplotlibImages.Count)"
}

foreach ($file in $expectedFiles) {
    $path = "assets\battle-plans-matplotlib\$file"
    if (-not (Test-Path $path)) {
        Write-Error "Missing matplotlib image: $file"
    }
    $size = (Get-Item $path).Length
    if ($size -lt 10KB) {
        Write-Error "$file is suspiciously small ($size bytes)"
    }
    Write-Host "✓ $file - $([math]::Round($size/1KB,1))KB"
}

# Step 5: Visual comparison check
Write-Host "`nStep 5: Manual validation required..."
Write-Host "CRITICAL: Compare matplotlib images to Wahapedia originals:"
Write-Host "  Wahapedia:   assets\battle-plans\"
Write-Host "  Matplotlib:  assets\battle-plans-matplotlib\"
Write-Host ""
Write-Host "Verify for EACH image:"
Write-Host "  - Deployment zones match"
Write-Host "  - Objective count matches"
Write-Host "  - Objective positions approximately match"
Write-Host ""
$confirm = Read-Host "Have you visually compared ALL 12 images? (yes/no)"
if ($confirm -ne "yes") {
    Write-Error "Visual validation required before proceeding"
}

Write-Host "`n" + "=" * 80
Write-Host "✓ Matplotlib diagrams generated and validated"
Write-Host "=" * 80
Write-Host "`nNext steps:"
Write-Host "  1. Review: explorer assets\battle-plans-matplotlib\"
Write-Host "  2. Test API: Invoke-WebRequest http://localhost/api/squire/battle-plans/gallery?image_version=matplotlib"
Write-Host "  3. Rebuild Docker: docker-compose build squig"
Write-Host "  4. Commit: git add assets/battle-plans-matplotlib scripts/generate_matplotlib_battleplans.py"

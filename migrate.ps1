<#
.SYNOPSIS
Migrates the Phoenix Tracker from playground to a permanent project location.
.DESCRIPTION
This script:
1. Creates the destination directory
2. Copies all source files (excluding temporary files, venv, logs)
3. Initializes a new Git repository
4. Creates a new virtual environment
5. Installs dependencies
6. Verifies the setup
.PARAMETER DestinationPath
The full path where you want to create the new project (e.g., "C:\Users\marku\Projects\phoenix-tracker")
.EXAMPLE
.\migrate.ps1 -DestinationPath "C:\Users\marku\Projects\phoenix-tracker"
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$DestinationPath
)
$ErrorActionPreference = "Stop"
$SourcePath = Get-Location
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phoenix Tracker Migration Assistant" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
# 1. Validate and Create Directory
if (Test-Path $DestinationPath) {
    Write-Warning "Destination directory already exists: $DestinationPath"
    $choice = Read-Host "Do you want to continue and potentially overwrite files? (y/N)"
    if ($choice.ToLower() -ne 'y') {
        Write-Host "Migration cancelled."
        exit
    }
} else {
    Write-Host "Creating directory: $DestinationPath"
    New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
}
# 2. Copy Files
Write-Host "Copying project files..." -ForegroundColor Yellow
# List of items to exclude
$Excludes = @(
    "__pycache__",
    "venv",
    ".git",
    ".idea",
    ".vscode",
    "*.log",
    "logs",
    "migrate.ps1" # Don't copy the migration script itself
)
# Get all items in source
$Items = Get-ChildItem -Path $SourcePath -Exclude $Excludes
foreach ($Item in $Items) {
    # Skip if it matches any exclude pattern (simple check)
    $Skip = $false
    foreach ($Exc in $Excludes) {
        if ($Item.Name -like $Exc) { $Skip = $true; break }
    }
    
    if (-not $Skip) {
        Write-Host "  Copying $($Item.Name)..."
        Copy-Item -Path $Item.FullName -Destination $DestinationPath -Recurse -Force
    }
}
# 3. Initialize Git
Write-Host "`nInitializing Git repository..." -ForegroundColor Yellow
Set-Location $DestinationPath
git init
# 4. Setup Virtual Environment
Write-Host "`nSetting up Python virtual environment..." -ForegroundColor Yellow
python -m venv venv
# 5. Install Dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\python -m pip install --upgrade pip
.\venv\Scripts\pip install -r requirements.txt
# 6. Final Checks
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "New project location: $DestinationPath"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. cd $DestinationPath"
Write-Host "2. .\venv\Scripts\activate"
Write-Host "3. python desktop_tracker.py"
Write-Host ""
Write-Host "Note: Your authentication token is stored in Windows Credential Manager"
Write-Host "and will work automatically in the new location."
Write-Host ""
# Return to original location
Set-Location $SourcePath

# PowerShell launcher that requests admin rights and navigates to project directory
# This script can be run from anywhere

# Request administrator privileges if not already admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Requesting administrator privileges..." -ForegroundColor Yellow
    
    # Get the script directory
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $setupScript = Join-Path $scriptDir "setup_network_autostart_simple.ps1"
    
    # Re-launch as administrator
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$setupScript`"" -Verb RunAs -WorkingDirectory $scriptDir
    exit
}

# Set console output encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================"
Write-Host "  Setup Auto-Start for Network Path"
Write-Host "========================================"
Write-Host ""

# Network path
$NetworkPath = "\\Desktop-1\новая папка\code\debt-track"

# Try to navigate to network path
Write-Host "Navigating to project directory..." -ForegroundColor Cyan
Write-Host "Path: $NetworkPath" -ForegroundColor Gray

try {
    # PowerShell supports UNC paths, so we can use Set-Location
    Set-Location -LiteralPath $NetworkPath -ErrorAction Stop
    Write-Host "Successfully navigated to project directory!" -ForegroundColor Green
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "ERROR: Cannot access network path!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please make sure:" -ForegroundColor Cyan
    Write-Host "  1. Network share is accessible" -ForegroundColor White
    Write-Host "  2. You can access it in File Explorer" -ForegroundColor White
    Write-Host "  3. Desktop-1 computer is on the network" -ForegroundColor White
    Write-Host ""
    Write-Host "Alternative: Map the network drive to a letter (e.g., Z:)" -ForegroundColor Yellow
    Write-Host "  Then navigate to: Z:\code\debt-track" -ForegroundColor Gray
    Write-Host ""
    pause
    exit 1
}

# Verify manage.py exists
if (-not (Test-Path "manage.py")) {
    Write-Host "ERROR: manage.py not found in current directory!" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    pause
    exit 1
}

# Now run the setup script
$setupScript = Join-Path $PSScriptRoot "setup_network_autostart_simple.ps1"
if (Test-Path $setupScript) {
    Write-Host "Running setup script..." -ForegroundColor Cyan
    Write-Host ""
    & $setupScript
} else {
    Write-Host "ERROR: setup_network_autostart_simple.ps1 not found!" -ForegroundColor Red
    Write-Host "Make sure all files are in the project directory." -ForegroundColor Yellow
    pause
    exit 1
}






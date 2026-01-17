# Simplified setup script - run this from the project directory
# This avoids encoding issues with network paths

# Set console output encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================"
Write-Host "  Setup Auto-Start for Network Path"
Write-Host "========================================"
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Get current directory (should be the project directory)
$ProjectPath = (Get-Location).Path

# Verify we're in the project directory
if (-not (Test-Path "$ProjectPath\manage.py")) {
    Write-Host "ERROR: manage.py not found in current directory!" -ForegroundColor Red
    Write-Host "Current directory: $ProjectPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please navigate to the project directory first:" -ForegroundColor Cyan
    Write-Host "  cd '\\Desktop-1\новая папка\code\debt-track'" -ForegroundColor Gray
    Write-Host "  .\setup_network_autostart_simple.ps1" -ForegroundColor Gray
    Write-Host ""
    pause
    exit 1
}

Write-Host "Project directory: $ProjectPath" -ForegroundColor Green
Write-Host ""

$TaskName = "PharmacyDebtTracker"

# Find Python executable
Write-Host "Step 1: Finding Python executable..."
$PythonCmd = $null

# Check for virtual environment first
$VenvPython = Join-Path $ProjectPath "venv\Scripts\python.exe"
$VenvPythonW = Join-Path $ProjectPath "venv\Scripts\pythonw.exe"
if (Test-Path $VenvPython) {
    $PythonCmd = $VenvPython
    Write-Host "Found virtual environment Python: $PythonCmd" -ForegroundColor Green
} elseif (Test-Path $VenvPythonW) {
    $PythonCmd = $VenvPythonW
    Write-Host "Found virtual environment Python: $PythonCmd" -ForegroundColor Green
} else {
    # Try system Python
    $PythonW = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    $Python = Get-Command python.exe -ErrorAction SilentlyContinue
    
    if ($PythonW) {
        $PythonCmd = $PythonW.Source
        Write-Host "Found system Python: $PythonCmd" -ForegroundColor Green
    } elseif ($Python) {
        $PythonCmd = $Python.Source
        Write-Host "Found system Python: $PythonCmd" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Python not found!" -ForegroundColor Red
        Write-Host "Please install Python or add it to PATH."
        pause
        exit 1
    }
}
Write-Host ""

# Remove existing task if it exists
Write-Host "Step 2: Removing existing task (if any)..."
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task." -ForegroundColor Yellow
}
Write-Host ""

# Create the action
Write-Host "Step 3: Creating scheduled task..."
try {
    $Action = New-ScheduledTaskAction -Execute $PythonCmd -Argument "manage.py runserver 0.0.0.0:8000" -WorkingDirectory $ProjectPath
    $Trigger = New-ScheduledTaskTrigger -AtLogOn
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    $Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Start Django Pharmacy Debt Tracker Server from network path" | Out-Null
    Write-Host "Task created successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create task!" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "Please create the task manually:" -ForegroundColor Yellow
    Write-Host "  1. Press Win+R, type: taskschd.msc"
    Write-Host "  2. Create Basic Task"
    Write-Host "  3. Name: $TaskName"
    Write-Host "  4. Trigger: When I log on"
    Write-Host "  5. Action: Start a program"
    Write-Host "  6. Program: $PythonCmd"
    Write-Host "  7. Arguments: manage.py runserver 0.0.0.0:8000"
    Write-Host "  8. Start in: $ProjectPath"
    Write-Host "  9. Check 'Run with highest privileges'"
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "  Setup Complete!"
Write-Host "========================================"
Write-Host ""
Write-Host "Task Name: $TaskName"
Write-Host "Project Path: $ProjectPath"
Write-Host "Python: $PythonCmd"
Write-Host ""
Write-Host "The server will start automatically when you log on."
Write-Host ""
Write-Host "To test: Open Task Scheduler, find '$TaskName', right-click and select 'Run'"
Write-Host "To remove: Run this command:"
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
Write-Host ""
pause








# PowerShell script to setup auto-start for Django server on network path
# Network path: \\Desktop-1\новая папка\code\debt-track

# Set console output encoding to UTF-8 to handle Cyrillic characters
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================"
Write-Host "  Setup Auto-Start for Network Path"
Write-Host "  \\Desktop-1\новая папка\code\debt-track"
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

$TaskName = "PharmacyDebtTracker"

# Try to detect network path - first check if we're already in the project directory
$NetworkPath = $null
$CurrentDir = Get-Location

# Check if we're already in the project directory
if (Test-Path "$CurrentDir\manage.py") {
    $NetworkPath = $CurrentDir.Path
    Write-Host "Found project in current directory: $NetworkPath" -ForegroundColor Cyan
} else {
    # Try the network path
    $NetworkPath = "\\Desktop-1\новая папка\code\debt-track"
    
    # Try alternative methods to access the path
    Write-Host "Step 1: Checking network path accessibility..."
    Write-Host "  Trying path: $NetworkPath" -ForegroundColor Gray
    
    # Method 1: Direct Test-Path
    $PathAccessible = $false
    try {
        $PathAccessible = Test-Path -LiteralPath $NetworkPath -ErrorAction Stop
    } catch {
        Write-Host "  Direct path test failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # Method 2: Try using Get-Item
    if (-not $PathAccessible) {
        try {
            $item = Get-Item -LiteralPath $NetworkPath -ErrorAction Stop
            $PathAccessible = $true
            Write-Host "  Path accessible via Get-Item" -ForegroundColor Green
        } catch {
            Write-Host "  Get-Item failed: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    # Method 3: Try using cmd /c dir
    if (-not $PathAccessible) {
        Write-Host "  Trying alternative access method..." -ForegroundColor Yellow
        $testResult = cmd /c "if exist `"$NetworkPath\manage.py`" (exit 0) else (exit 1)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            $PathAccessible = $true
            Write-Host "  Path accessible via cmd" -ForegroundColor Green
        }
    }
    
    if (-not $PathAccessible) {
        Write-Host ""
        Write-Host "ERROR: Cannot access network path!" -ForegroundColor Red
        Write-Host "  Path: $NetworkPath" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please try one of these solutions:" -ForegroundColor Cyan
        Write-Host "  1. Navigate to the project folder first:" -ForegroundColor White
        Write-Host "     cd '\\Desktop-1\новая папка\code\debt-track'" -ForegroundColor Gray
        Write-Host "     .\setup_network_autostart.ps1" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  2. Map the network drive to a letter (e.g., Z:)" -ForegroundColor White
        Write-Host "     Then update the script to use the mapped drive" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  3. Make sure:" -ForegroundColor White
        Write-Host "     - Network share is accessible" -ForegroundColor Gray
        Write-Host "     - You have read/write permissions" -ForegroundColor Gray
        Write-Host "     - Desktop-1 computer is on the network" -ForegroundColor Gray
        Write-Host "     - You can access it in File Explorer" -ForegroundColor Gray
        Write-Host ""
        pause
        exit 1
    }
}

# Verify manage.py exists
if (-not (Test-Path -LiteralPath "$NetworkPath\manage.py")) {
    Write-Host "ERROR: manage.py not found in: $NetworkPath" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Network path is accessible!" -ForegroundColor Green
Write-Host "  Project path: $NetworkPath" -ForegroundColor Cyan
Write-Host ""

# Find Python executable
Write-Host "Step 2: Finding Python executable..."
$PythonCmd = $null

# Check for virtual environment first
$VenvPython = Join-Path $NetworkPath "venv\Scripts\python.exe"
$VenvPythonW = Join-Path $NetworkPath "venv\Scripts\pythonw.exe"
if (Test-Path -LiteralPath $VenvPython) {
    $PythonCmd = $VenvPython
    Write-Host "Found virtual environment Python: $PythonCmd" -ForegroundColor Green
} elseif (Test-Path -LiteralPath $VenvPythonW) {
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
Write-Host "Step 3: Removing existing task (if any)..."
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task." -ForegroundColor Yellow
}
Write-Host ""

# Create the action - use LiteralPath for network paths with special characters
$Action = New-ScheduledTaskAction -Execute $PythonCmd -Argument "manage.py runserver 0.0.0.0:8000" -WorkingDirectory (Resolve-Path -LiteralPath $NetworkPath).Path

# Create the trigger (when user logs on)
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# Create task settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create task principal (run with highest privileges)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Register the task
Write-Host "Step 4: Creating scheduled task..."
try {
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
    Write-Host "  8. Start in: $NetworkPath"
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
Write-Host "Network Path: $NetworkPath"
Write-Host "Python: $PythonCmd"
Write-Host ""
Write-Host "The server will start automatically when you log on."
Write-Host ""
Write-Host "To test: Open Task Scheduler, find '$TaskName', right-click and select 'Run'"
Write-Host "To remove: Run this command:"
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
Write-Host ""
pause


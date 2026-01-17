# Final, most robust setup script
# This script handles all edge cases and provides clear error messages

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

Write-Host "========================================"
Write-Host "  Auto-Start Setup (Final Version)"
Write-Host "========================================"
Write-Host ""

# Step 1: Check admin rights
Write-Host "Step 1: Checking administrator privileges..." -ForegroundColor Cyan
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "  1. Close this window" -ForegroundColor White
    Write-Host "  2. Right-click this file" -ForegroundColor White
    Write-Host "  3. Select 'Run with PowerShell' or 'Run as administrator'" -ForegroundColor White
    Write-Host ""
    Write-Host "Or run PowerShell as Administrator and execute:" -ForegroundColor Yellow
    Write-Host "  cd '\\Desktop-1\новая папка\code\debt-track'" -ForegroundColor Gray
    Write-Host "  .\setup_autostart_FINAL.ps1" -ForegroundColor Gray
    pause
    exit 1
}
Write-Host "  ✓ Administrator privileges confirmed" -ForegroundColor Green
Write-Host ""

# Step 2: Set execution policy if needed
Write-Host "Step 2: Checking execution policy..." -ForegroundColor Cyan
$policy = Get-ExecutionPolicy
if ($policy -eq "Restricted") {
    Write-Host "  Execution policy is Restricted. Attempting to fix..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "  ✓ Execution policy updated" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ Could not change execution policy automatically" -ForegroundColor Yellow
        Write-Host "  Please run manually: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White
    }
} else {
    Write-Host "  ✓ Execution policy is OK ($policy)" -ForegroundColor Green
}
Write-Host ""

# Step 3: Try to access network path
Write-Host "Step 3: Accessing network path..." -ForegroundColor Cyan
$NetworkPath = "\\Desktop-1\новая папка\code\debt-track"
$ProjectPath = $null

# Try current directory first
$CurrentDir = Get-Location
if (Test-Path "$CurrentDir\manage.py") {
    $ProjectPath = $CurrentDir.Path
    Write-Host "  ✓ Found project in current directory: $ProjectPath" -ForegroundColor Green
} else {
    # Try network path
    Write-Host "  Trying network path: $NetworkPath" -ForegroundColor Gray
    
    # Multiple methods to access UNC path
    $PathAccessible = $false
    $Methods = @(
        { Test-Path -LiteralPath $NetworkPath },
        { Get-Item -LiteralPath $NetworkPath | Out-Null },
        { [System.IO.Directory]::Exists($NetworkPath) }
    )
    
    foreach ($method in $Methods) {
        try {
            & $method
            $PathAccessible = $true
            $ProjectPath = $NetworkPath
            break
        } catch {
            # Continue to next method
        }
    }
    
    if ($PathAccessible) {
        Write-Host "  ✓ Network path is accessible" -ForegroundColor Green
        Set-Location -LiteralPath $NetworkPath
    } else {
        Write-Host "  ✗ Cannot access network path!" -ForegroundColor Red
        Write-Host ""
        Write-Host "SOLUTION: Map the network drive first:" -ForegroundColor Yellow
        Write-Host "  1. Open Command Prompt as Administrator" -ForegroundColor White
        Write-Host "  2. Run: net use Z: `"$NetworkPath`"" -ForegroundColor Gray
        Write-Host "  3. Then run this script again from: Z:\code\debt-track" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Or try:" -ForegroundColor Yellow
        Write-Host "  1. Open File Explorer" -ForegroundColor White
        Write-Host "  2. Navigate to: $NetworkPath" -ForegroundColor Gray
        Write-Host "  3. Right-click this script → Run with PowerShell" -ForegroundColor White
        Write-Host ""
        pause
        exit 1
    }
}

# Verify manage.py
if (-not (Test-Path "$ProjectPath\manage.py")) {
    Write-Host "ERROR: manage.py not found in: $ProjectPath" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  ✓ manage.py found" -ForegroundColor Green
Write-Host ""

# Step 4: Find Python
Write-Host "Step 4: Finding Python executable..." -ForegroundColor Cyan
$PythonCmd = $null

# Check venv first
$VenvPythonW = Join-Path $ProjectPath "venv\Scripts\pythonw.exe"
$VenvPython = Join-Path $ProjectPath "venv\Scripts\python.exe"
if (Test-Path $VenvPythonW) {
    $PythonCmd = $VenvPythonW
    Write-Host "  ✓ Found virtual environment: $PythonCmd" -ForegroundColor Green
} elseif (Test-Path $VenvPython) {
    $PythonCmd = $VenvPython
    Write-Host "  ✓ Found virtual environment: $PythonCmd" -ForegroundColor Green
} else {
    # System Python
    $PythonW = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    $Python = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($PythonW) {
        $PythonCmd = $PythonW.Source
        Write-Host "  ✓ Found system Python: $PythonCmd" -ForegroundColor Green
    } elseif ($Python) {
        $PythonCmd = $Python.Source
        Write-Host "  ✓ Found system Python: $PythonCmd" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Python not found!" -ForegroundColor Red
        Write-Host "  Please install Python or ensure it's in PATH" -ForegroundColor Yellow
        pause
        exit 1
    }
}
Write-Host ""

# Step 5: Create scheduled task
Write-Host "Step 5: Creating scheduled task..." -ForegroundColor Cyan
$TaskName = "PharmacyDebtTracker"

# Remove existing task
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "  Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

try {
    $Action = New-ScheduledTaskAction -Execute $PythonCmd -Argument "manage.py runserver 0.0.0.0:8000" -WorkingDirectory $ProjectPath
    $Trigger = New-ScheduledTaskTrigger -AtLogOn
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    $Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Start Django Pharmacy Debt Tracker Server" | Out-Null
    
    Write-Host "  ✓ Task created successfully!" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to create task!" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please create the task manually:" -ForegroundColor Yellow
    Write-Host "  1. Win+R → taskschd.msc" -ForegroundColor White
    Write-Host "  2. Create Basic Task → Name: $TaskName" -ForegroundColor White
    Write-Host "  3. Trigger: When I log on" -ForegroundColor White
    Write-Host "  4. Action: Start program" -ForegroundColor White
    Write-Host "  5. Program: $PythonCmd" -ForegroundColor White
    Write-Host "  6. Arguments: manage.py runserver 0.0.0.0:8000" -ForegroundColor White
    Write-Host "  7. Start in: $ProjectPath" -ForegroundColor White
    Write-Host "  8. Properties → Run with highest privileges" -ForegroundColor White
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "  Setup Complete!"
Write-Host "========================================"
Write-Host ""
Write-Host "Task Name: $TaskName" -ForegroundColor Cyan
Write-Host "Project Path: $ProjectPath" -ForegroundColor Cyan
Write-Host "Python: $PythonCmd" -ForegroundColor Cyan
Write-Host ""
Write-Host "The server will start automatically when you log on." -ForegroundColor Green
Write-Host ""
Write-Host "To test:" -ForegroundColor Yellow
Write-Host "  1. Open Task Scheduler (Win+R → taskschd.msc)" -ForegroundColor White
Write-Host "  2. Find '$TaskName'" -ForegroundColor White
Write-Host "  3. Right-click → Run" -ForegroundColor White
Write-Host "  4. Open browser: http://127.0.0.1:8000" -ForegroundColor White
Write-Host ""
pause





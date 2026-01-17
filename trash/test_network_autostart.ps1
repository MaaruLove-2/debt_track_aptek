# Test script to verify network path and auto-start setup

Write-Host "========================================"
Write-Host "  Testing Network Path Auto-Start Setup"
Write-Host "========================================"
Write-Host ""

$NetworkPath = "\\Desktop-1\новая папка\code\debt-track"
$TestResults = @()

# Test 1: Network path accessibility
Write-Host "Test 1: Checking network path accessibility..."
if (Test-Path $NetworkPath) {
    Write-Host "  ✓ Network path is accessible" -ForegroundColor Green
    $TestResults += "Network Path: PASS"
} else {
    Write-Host "  ✗ Network path is NOT accessible" -ForegroundColor Red
    Write-Host "    Path: $NetworkPath" -ForegroundColor Yellow
    $TestResults += "Network Path: FAIL"
}

# Test 2: manage.py exists
Write-Host ""
Write-Host "Test 2: Checking for manage.py..."
if (Test-Path "$NetworkPath\manage.py") {
    Write-Host "  ✓ manage.py found" -ForegroundColor Green
    $TestResults += "manage.py: PASS"
} else {
    Write-Host "  ✗ manage.py NOT found" -ForegroundColor Red
    $TestResults += "manage.py: FAIL"
}

# Test 3: Python availability
Write-Host ""
Write-Host "Test 3: Checking Python availability..."
$PythonW = Get-Command pythonw.exe -ErrorAction SilentlyContinue
$Python = Get-Command python.exe -ErrorAction SilentlyContinue
if ($PythonW -or $Python) {
    if ($PythonW) {
        Write-Host "  ✓ pythonw.exe found: $($PythonW.Source)" -ForegroundColor Green
    } else {
        Write-Host "  ✓ python.exe found: $($Python.Source)" -ForegroundColor Green
    }
    $TestResults += "Python: PASS"
} else {
    Write-Host "  ✗ Python NOT found in PATH" -ForegroundColor Red
    $TestResults += "Python: FAIL"
}

# Test 4: Virtual environment
Write-Host ""
Write-Host "Test 4: Checking virtual environment..."
if (Test-Path "$NetworkPath\venv\Scripts\python.exe") {
    Write-Host "  ✓ Virtual environment found" -ForegroundColor Green
    Write-Host "    Path: $NetworkPath\venv\Scripts\python.exe" -ForegroundColor Cyan
    $TestResults += "Virtual Environment: PASS"
} else {
    Write-Host "  ⚠ Virtual environment NOT found (will use system Python)" -ForegroundColor Yellow
    $TestResults += "Virtual Environment: NOT FOUND"
}

# Test 5: Task Scheduler task
Write-Host ""
Write-Host "Test 5: Checking Task Scheduler task..."
$TaskName = "PharmacyDebtTracker"
$Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($Task) {
    Write-Host "  ✓ Task Scheduler task found: $TaskName" -ForegroundColor Green
    Write-Host "    State: $($Task.State)" -ForegroundColor Cyan
    $TestResults += "Task Scheduler: PASS"
} else {
    Write-Host "  ✗ Task Scheduler task NOT found" -ForegroundColor Red
    Write-Host "    Run setup_network_autostart.ps1 to create it" -ForegroundColor Yellow
    $TestResults += "Task Scheduler: NOT FOUND"
}

# Test 6: Server port availability
Write-Host ""
Write-Host "Test 6: Checking if port 8000 is available..."
$PortInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($PortInUse) {
    Write-Host "  ⚠ Port 8000 is already in use" -ForegroundColor Yellow
    Write-Host "    This might mean the server is already running" -ForegroundColor Cyan
    $TestResults += "Port 8000: IN USE"
} else {
    Write-Host "  ✓ Port 8000 is available" -ForegroundColor Green
    $TestResults += "Port 8000: AVAILABLE"
}

# Summary
Write-Host ""
Write-Host "========================================"
Write-Host "  Test Summary"
Write-Host "========================================"
foreach ($result in $TestResults) {
    if ($result -match "PASS") {
        Write-Host "  ✓ $result" -ForegroundColor Green
    } elseif ($result -match "FAIL") {
        Write-Host "  ✗ $result" -ForegroundColor Red
    } else {
        Write-Host "  ⚠ $result" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "  Recommendations"
Write-Host "========================================"

if ($TestResults -match "FAIL") {
    Write-Host "  ⚠ Some tests failed. Please fix the issues above." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Next steps:" -ForegroundColor Yellow
    Write-Host "    1. Make sure network path is accessible"
    Write-Host "    2. Run setup_network_autostart.ps1 as Administrator"
    Write-Host "    3. Test the task manually in Task Scheduler"
} else {
    Write-Host "  ✓ All critical tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Your auto-start setup should work correctly." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  To test:" -ForegroundColor Yellow
    Write-Host "    1. Open Task Scheduler"
    Write-Host "    2. Find 'PharmacyDebtTracker' task"
    Write-Host "    3. Right-click → Run"
    Write-Host "    4. Check if server starts: http://127.0.0.1:8000"
}

Write-Host ""
pause








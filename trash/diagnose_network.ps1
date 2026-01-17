# Diagnostic script to check network path and setup issues
# Run this first to see what's wrong

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================"
Write-Host "  Network Path Diagnostic Tool"
Write-Host "========================================"
Write-Host ""

$NetworkPath = "\\Desktop-1\новая папка\code\debt-track"
$Issues = @()
$Success = @()

# Test 1: Check if running as admin
Write-Host "Test 1: Administrator privileges..." -ForegroundColor Cyan
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "  ✓ Running as Administrator" -ForegroundColor Green
    $Success += "Admin: OK"
} else {
    Write-Host "  ✗ NOT running as Administrator" -ForegroundColor Red
    $Issues += "Need Administrator privileges"
}
Write-Host ""

# Test 2: Check PowerShell execution policy
Write-Host "Test 2: PowerShell execution policy..." -ForegroundColor Cyan
$policy = Get-ExecutionPolicy
Write-Host "  Current policy: $policy" -ForegroundColor Yellow
if ($policy -eq "Restricted") {
    Write-Host "  ✗ Execution policy is Restricted" -ForegroundColor Red
    $Issues += "Execution policy is Restricted - scripts won't run"
    Write-Host "  Fix: Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Execution policy allows scripts" -ForegroundColor Green
    $Success += "Execution Policy: OK"
}
Write-Host ""

# Test 3: Check network path accessibility
Write-Host "Test 3: Network path accessibility..." -ForegroundColor Cyan
Write-Host "  Testing: $NetworkPath" -ForegroundColor Gray

# Try multiple methods
$PathOK = $false
$Method = ""

# Method 1: Test-Path
try {
    if (Test-Path -LiteralPath $NetworkPath -ErrorAction Stop) {
        $PathOK = $true
        $Method = "Test-Path"
    }
} catch {
    Write-Host "  Test-Path failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Method 2: Get-Item
if (-not $PathOK) {
    try {
        $item = Get-Item -LiteralPath $NetworkPath -ErrorAction Stop
        $PathOK = $true
        $Method = "Get-Item"
    } catch {
        Write-Host "  Get-Item failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Method 3: cmd dir
if (-not $PathOK) {
    Write-Host "  Trying cmd /c dir..." -ForegroundColor Yellow
    $result = cmd /c "dir `"$NetworkPath`" 2>&1"
    if ($LASTEXITCODE -eq 0) {
        $PathOK = $true
        $Method = "cmd dir"
    }
}

# Method 4: net use
if (-not $PathOK) {
    Write-Host "  Trying net use..." -ForegroundColor Yellow
    $result = net use 2>&1 | Select-String "Desktop-1"
    if ($result) {
        Write-Host "  Network connection exists but path might be wrong" -ForegroundColor Yellow
    }
}

if ($PathOK) {
    Write-Host "  ✓ Network path is accessible (via $Method)" -ForegroundColor Green
    $Success += "Network Path: OK"
} else {
    Write-Host "  ✗ Network path is NOT accessible" -ForegroundColor Red
    $Issues += "Cannot access network path"
    Write-Host ""
    Write-Host "  Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "    1. Open File Explorer and try to navigate to: $NetworkPath" -ForegroundColor White
    Write-Host "    2. Check if Desktop-1 computer is on and accessible" -ForegroundColor White
    Write-Host "    3. Try mapping the drive: net use Z: `"$NetworkPath`"" -ForegroundColor White
}
Write-Host ""

# Test 4: Check for manage.py
Write-Host "Test 4: Checking for manage.py..." -ForegroundColor Cyan
if ($PathOK) {
    try {
        $managePy = Join-Path $NetworkPath "manage.py"
        if (Test-Path -LiteralPath $managePy) {
            Write-Host "  ✓ manage.py found" -ForegroundColor Green
            $Success += "manage.py: OK"
        } else {
            Write-Host "  ✗ manage.py NOT found" -ForegroundColor Red
            $Issues += "manage.py not found"
        }
    } catch {
        Write-Host "  ✗ Error checking for manage.py: $($_.Exception.Message)" -ForegroundColor Red
        $Issues += "Error accessing manage.py"
    }
} else {
    Write-Host "  ⚠ Skipped (network path not accessible)" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Check Python
Write-Host "Test 5: Checking Python..." -ForegroundColor Cyan
$PythonFound = $false
$PythonPath = ""

# Check system Python
$PythonW = Get-Command pythonw.exe -ErrorAction SilentlyContinue
$Python = Get-Command python.exe -ErrorAction SilentlyContinue

if ($PythonW) {
    $PythonFound = $true
    $PythonPath = $PythonW.Source
    Write-Host "  ✓ pythonw.exe found: $PythonPath" -ForegroundColor Green
} elseif ($Python) {
    $PythonFound = $true
    $PythonPath = $Python.Source
    Write-Host "  ✓ python.exe found: $PythonPath" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python NOT found in PATH" -ForegroundColor Red
    $Issues += "Python not in PATH"
}

# Check venv
if ($PathOK) {
    $VenvPython = Join-Path $NetworkPath "venv\Scripts\python.exe"
    $VenvPythonW = Join-Path $NetworkPath "venv\Scripts\pythonw.exe"
    if (Test-Path -LiteralPath $VenvPythonW) {
        Write-Host "  ✓ Virtual environment pythonw.exe found" -ForegroundColor Green
        $PythonPath = $VenvPythonW
        $PythonFound = $true
    } elseif (Test-Path -LiteralPath $VenvPython) {
        Write-Host "  ✓ Virtual environment python.exe found" -ForegroundColor Green
        $PythonPath = $VenvPython
        $PythonFound = $true
    }
}

if ($PythonFound) {
    $Success += "Python: OK"
} else {
    $Issues += "Python not found"
}
Write-Host ""

# Summary
Write-Host "========================================"
Write-Host "  Diagnostic Summary"
Write-Host "========================================"
Write-Host ""

if ($Success.Count -gt 0) {
    Write-Host "✓ Working:" -ForegroundColor Green
    foreach ($item in $Success) {
        Write-Host "  - $item" -ForegroundColor Green
    }
    Write-Host ""
}

if ($Issues.Count -gt 0) {
    Write-Host "✗ Issues found:" -ForegroundColor Red
    foreach ($item in $Issues) {
        Write-Host "  - $item" -ForegroundColor Red
    }
    Write-Host ""
    
    Write-Host "Recommended fixes:" -ForegroundColor Yellow
    if ($Issues -contains "Need Administrator privileges") {
        Write-Host "  1. Right-click PowerShell → Run as Administrator" -ForegroundColor White
    }
    if ($Issues -contains "Execution policy is Restricted") {
        Write-Host "  2. Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White
    }
    if ($Issues -contains "Cannot access network path") {
        Write-Host "  3. Try mapping the network drive:" -ForegroundColor White
        Write-Host "     net use Z: `"$NetworkPath`"" -ForegroundColor Gray
        Write-Host "     Then use: Z:\code\debt-track" -ForegroundColor Gray
    }
} else {
    Write-Host "✓ All tests passed! Setup should work." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next step: Run setup_autostart_as_admin.ps1" -ForegroundColor Cyan
}

Write-Host ""
pause





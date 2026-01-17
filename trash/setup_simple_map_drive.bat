@echo off
REM Simple setup that maps network drive first, then runs setup
REM This is the most reliable method for UNC paths

echo ========================================
echo   Simple Auto-Start Setup
echo ========================================
echo.

REM Check admin
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Map network drive to Z:
echo Step 1: Mapping network drive...
net use Z: "\\Desktop-1\новая папка" /persistent:yes
if errorlevel 1 (
    echo WARNING: Could not map drive. Trying to continue anyway...
) else (
    echo   Drive Z: mapped successfully
)
echo.

REM Change to project directory
echo Step 2: Navigating to project directory...
cd /d Z:\code\debt-track
if errorlevel 1 (
    echo ERROR: Cannot access project directory!
    echo.
    echo Please check:
    echo   1. Network path is accessible
    echo   2. Desktop-1 computer is on
    echo   3. You have permissions
    pause
    exit /b 1
)
echo   Current directory: %CD%
echo.

REM Check for manage.py
if not exist "manage.py" (
    echo ERROR: manage.py not found!
    echo Current directory: %CD%
    pause
    exit /b 1
)
echo   manage.py found
echo.

REM Run PowerShell setup script
echo Step 3: Running PowerShell setup script...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "setup_autostart_FINAL.ps1"

REM Keep drive mapped
echo.
echo Note: Network drive Z: is now mapped permanently
echo You can use Z:\code\debt-track instead of the UNC path
echo.
pause





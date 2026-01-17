@echo off
REM Launcher script to run PowerShell setup script as Administrator
REM This works around CMD's UNC path limitation

REM Get the script directory
set "SCRIPT_DIR=%~dp0"

REM Always request admin rights and run PowerShell script
echo ========================================
echo   Setup Auto-Start for Network Path
echo ========================================
echo.
echo Requesting administrator privileges...
echo.

REM Re-launch PowerShell as administrator
powershell -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%SCRIPT_DIR%setup_autostart_as_admin.ps1\"' -Verb RunAs"

exit /b


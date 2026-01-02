@echo off
REM Create desktop shortcut silently
set "SCRIPT_DIR=%~dp0"
powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File "%SCRIPT_DIR%create_desktop_shortcut.ps1" -ProjectPath "%SCRIPT_DIR%"
exit /b


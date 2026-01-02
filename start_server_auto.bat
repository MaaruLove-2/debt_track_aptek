@echo off
REM Auto-start server script - runs in background with minimal window

cd /d %~dp0

REM Start server in new hidden window using start command
start "" /MIN pythonw.exe manage.py runserver 0.0.0.0:8000

REM If pythonw.exe doesn't work, try python.exe with window minimized
if errorlevel 1 (
    start "" /MIN python.exe manage.py runserver 0.0.0.0:8000
)

REM Exit immediately
exit




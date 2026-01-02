@echo off
REM This script starts the server in the background
REM The window will close automatically, but server keeps running

cd /d %~dp0

REM Start server in background using pythonw (no window)
start /B pythonw.exe manage.py runserver 0.0.0.0:8000

REM Wait a moment to ensure server started
timeout /t 2 /nobreak >nul

echo Server started in background!
echo.
echo To stop the server, use Task Manager or run:
echo   taskkill /F /IM pythonw.exe
echo.
pause





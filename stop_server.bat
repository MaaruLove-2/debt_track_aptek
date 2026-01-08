

@echo off
echo Stopping Pharmacy Server...
echo.

REM Find process using port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing process %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo Server stopped.
echo.
pause



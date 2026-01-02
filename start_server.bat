@echo off
REM Start Django development server and open browser
cd /d "%~dp0"
echo ========================================
echo   Aptek Borc Izleyicisi
echo   Starting Django Server...
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if manage.py exists
if not exist "manage.py" (
    echo ERROR: manage.py not found!
    echo Please make sure you're running this from the project directory.
    pause
    exit /b 1
)

REM Start the Django server in a new window
start "Django Server - Aptek Borc Izleyicisi" cmd /k "python manage.py runserver"

REM Wait a moment for server to start
timeout /t 4 /nobreak >nul

REM Open browser
start http://127.0.0.1:8000

echo.
echo ========================================
echo   Server started successfully!
echo   URL: http://127.0.0.1:8000
echo ========================================
echo.
echo The server window will stay open.
echo Close this window - the server will continue running.
echo.
timeout /t 2 /nobreak >nul

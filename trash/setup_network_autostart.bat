@echo off
REM Setup auto-start for Django server on network path
REM This script creates a Task Scheduler task for network UNC path

echo ========================================
echo   Setup Auto-Start for Network Path
echo   \\Desktop-1\новая папка\code\debt-track
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

set "TASK_NAME=PharmacyDebtTracker"
set "NETWORK_PATH=\\Desktop-1\новая папка\code\debt-track"
set "VBS_SCRIPT=%NETWORK_PATH%\start_server_network.vbs"

REM Check if network path is accessible
if not exist "%NETWORK_PATH%\manage.py" (
    echo ERROR: Cannot access network path: %NETWORK_PATH%
    echo Please make sure:
    echo   1. Network share is accessible
    echo   2. You have read/write permissions
    echo   3. Desktop-1 computer is on the network
    pause
    exit /b 1
)

echo Step 1: Creating Task Scheduler task...
echo.

REM Delete existing task if it exists
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

REM Find Python executable
where pythonw.exe >nul 2>&1
if errorlevel 1 (
    where python.exe >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python not found in PATH!
        echo Please install Python or add it to PATH.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python.exe"
) else (
    set "PYTHON_CMD=pythonw.exe"
)

REM Check for virtual environment
if exist "%NETWORK_PATH%\venv\Scripts\python.exe" (
    set "PYTHON_CMD=%NETWORK_PATH%\venv\Scripts\python.exe"
) else if exist "%NETWORK_PATH%\venv\Scripts\pythonw.exe" (
    set "PYTHON_CMD=%NETWORK_PATH%\venv\Scripts\pythonw.exe"
)

echo Using Python: %PYTHON_CMD%
echo.

REM Create task using schtasks command
echo Creating scheduled task...
schtasks /Create /TN "%TASK_NAME%" ^
    /TR "\"%PYTHON_CMD%\" manage.py runserver 0.0.0.0:8000" ^
    /SC ONLOGON ^
    /RL HIGHEST ^
    /F ^
    /IT ^
    /SD "%NETWORK_PATH%"

REM Set the working directory in task properties
schtasks /Change /TN "%TASK_NAME%" /SD "%NETWORK_PATH%" >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create task!
    echo.
    echo Please create the task manually using Task Scheduler:
    echo   1. Press Win+R, type: taskschd.msc
    echo   2. Create Basic Task
    echo   3. Name: PharmacyDebtTracker
    echo   4. Trigger: When I log on
    echo   5. Action: Start a program
    echo   6. Program: %PYTHON_CMD%
    echo   7. Arguments: manage.py runserver 0.0.0.0:8000
    echo   8. Start in: %NETWORK_PATH%
    echo   9. Check "Run with highest privileges"
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Task created successfully!
echo ========================================
echo.
echo Task Name: %TASK_NAME%
echo Network Path: %NETWORK_PATH%
echo Python: %PYTHON_CMD%
echo.
echo The server will start automatically when you log on.
echo.
echo To test: Right-click the task in Task Scheduler and select "Run"
echo To remove: Run: schtasks /Delete /TN "%TASK_NAME%" /F
echo.
pause


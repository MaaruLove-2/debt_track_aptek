@echo off
REM Auto-start server script for network UNC path
REM Network path: \\Desktop-1\новая папка\code\debt-track

REM Network UNC path
set "NETWORK_PATH=\\Desktop-1\новая папка\code\debt-track"

REM Wait for network to be ready (important at boot time)
timeout /t 5 /nobreak >nul

REM Change to network directory
cd /d "%NETWORK_PATH%"

REM Check if path is accessible
if not exist "manage.py" (
    echo ERROR: Cannot access network path: %NETWORK_PATH%
    echo Network might not be ready yet. Please check network connection.
    pause
    exit /b 1
)

REM Check for virtual environment
if exist "venv\Scripts\python.exe" (
    set "PYTHON_CMD=venv\Scripts\python.exe"
) else if exist "venv\Scripts\pythonw.exe" (
    set "PYTHON_CMD=venv\Scripts\pythonw.exe"
) else (
    REM Try to find Python in system
    where pythonw.exe >nul 2>&1
    if errorlevel 1 (
        set "PYTHON_CMD=python.exe"
    ) else (
        set "PYTHON_CMD=pythonw.exe"
    )
)

REM Start server in minimized window (hidden)
start "" /MIN "%PYTHON_CMD%" manage.py runserver 192.168.100.11:8000

REM Log to file
echo %date% %time% - Server started from network path >> "%NETWORK_PATH%\server_log.txt"

REM Exit immediately
exit


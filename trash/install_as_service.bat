@echo off
echo ========================================
echo   Installing Pharmacy Server as Service
echo ========================================
echo.
echo This will install the server to run automatically
echo in the background without showing a window.
echo.
pause

REM Check if NSSM is available
where nssm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo NSSM (Non-Sucking Service Manager) not found.
    echo Downloading NSSM...
    echo.
    echo Please download NSSM from: https://nssm.cc/download
    echo Extract nssm.exe to this folder, then run this script again.
    echo.
    pause
    exit /b 1
)

REM Get the current directory
set SCRIPT_DIR=%~dp0
set PYTHON_PATH=python.exe
set SERVER_PATH=%SCRIPT_DIR%manage.py

REM Install as Windows Service
echo Installing service...
nssm install PharmacyServer "%PYTHON_PATH%" "manage.py runserver 0.0.0.0:8000"
nssm set PharmacyServer AppDirectory "%SCRIPT_DIR%"
nssm set PharmacyServer DisplayName "Pharmacy Website Server"
nssm set PharmacyServer Description "Pharmacy Debt Tracking System Server"
nssm set PharmacyServer Start SERVICE_AUTO_START

echo.
echo Service installed successfully!
echo.
echo To start the service now, run:
echo   nssm start PharmacyServer
echo.
echo To stop the service:
echo   nssm stop PharmacyServer
echo.
echo To remove the service:
echo   nssm remove PharmacyServer confirm
echo.
pause





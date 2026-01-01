@echo off
echo ========================================
echo   Pharmacy Server Status Check
echo ========================================
echo.

echo Checking if server is running...
echo.

REM Check for Python processes
tasklist | findstr /I "python pythonw" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python processes found
    tasklist | findstr /I "python pythonw"
) else (
    echo [NOT RUNNING] No Python processes found
)

echo.
echo Checking port 8000...
netstat -an | findstr :8000 >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Port 8000 is in use (server is likely running)
    netstat -an | findstr :8000
) else (
    echo [NOT RUNNING] Port 8000 is not in use
)

echo.
echo ========================================
echo.
echo To test: Open browser and go to:
echo   http://YOUR-SERVER-IP:8000
echo.
pause



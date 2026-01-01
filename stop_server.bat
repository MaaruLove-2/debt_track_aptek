@echo off
echo Stopping Pharmacy Server...
echo.

REM Kill all Python processes running manage.py
taskkill /F /FI "WINDOWTITLE eq *manage.py*" /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM python.exe /FI "COMMANDLINE eq *manage.py*" /T >nul 2>&1

echo Server stopped!
echo.
pause



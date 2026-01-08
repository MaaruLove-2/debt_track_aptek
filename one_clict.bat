@REM @echo off
@REM REM =====================================================
@REM REM One-click silent Django launcher - FIXED & RELIABLE
@REM REM =====================================================

@REM REM ===== CONFIG =====
@REM set PROJECT_PATH=D:\shared\code\debt-track
@REM set VENV_NAME=venv2

@REM set SERVER_IP=192.168.100.11
@REM set PORT=8000

@REM REM ===== Change to project directory =====
@REM pushd "%PROJECT_PATH%" || (
@REM     echo Failed to access project folder.
@REM     pause
@REM     exit /b 1
@REM )


@REM REM ===== Locate Python executable =====
@REM set PYTHON_EXE=%PROJECT_PATH%\%VENV_NAME%\Scripts\python.exe
@REM if not exist "%PYTHON_EXE%" (
@REM     echo Python executable not found in venv2!
@REM     pause
@REM     popd
@REM     exit /b 1
@REM )

@REM REM ===== Check if server is already running =====
@REM netstat -an | findstr ":%PORT% " >nul
@REM if %errorlevel%==0 (
@REM     start "" "http://%SERVER_IP%:%PORT%"
@REM     popd
@REM     exit /b 0
@REM )

@REM REM ===== Start Django server (SAFE WAY) =====
@REM REM Get current directory (pushd maps network path to drive letter like Z:)
@REM set CURRENT_DIR=%CD%
@REM REM Build Python path using current directory (mapped drive)
@REM set PYTHON_FULL=%CURRENT_DIR%\%VENV_NAME%\Scripts\python.exe
@REM REM Verify Python exists at this location
@REM if not exist "%PYTHON_FULL%" (
@REM     echo Error: Python not found at %PYTHON_FULL%
@REM     pause
@REM     popd
@REM     exit /b 1
@REM )
@REM REM Create a startup batch file in the project directory
@REM set START_BAT=%CURRENT_DIR%\__start_server.bat
@REM echo @echo off > "%START_BAT%"
@REM echo cd /d "%CURRENT_DIR%" >> "%START_BAT%"
@REM echo echo Starting Django server... >> "%START_BAT%"
@REM echo "%PYTHON_FULL%" manage.py runserver 0.0.0.0:%PORT% >> "%START_BAT%"
@REM echo echo. >> "%START_BAT%"
@REM echo echo Server stopped. Press any key to close... >> "%START_BAT%"
@REM echo pause ^>nul >> "%START_BAT%"
@REM REM Start server in a visible window so we can see errors
@REM start "" "%START_BAT%"
@REM timeout /t 3 /nobreak >nul


@REM REM ===== Wait for server to start =====
@REM set ATTEMPTS=0
@REM :WAIT_LOOP
@REM timeout /t 1 /nobreak >nul
@REM netstat -an | findstr ":%PORT% " >nul
@REM if %errorlevel%==0 goto SERVER_READY
@REM set /a ATTEMPTS+=1
@REM if %ATTEMPTS% geq 15 goto SERVER_READY
@REM goto WAIT_LOOP

@REM :SERVER_READY
@REM REM ===== Open browser =====
@REM start "" "http://%SERVER_IP%:%PORT%"

@REM popd
@REM exit /b 0

@echo off
wscript "D:\shared\code\debt-track\start.vbs
exit

@echo off
REM Simple batch file to create desktop shortcut
REM This creates a shortcut that runs silently

echo Creating desktop shortcut...
echo.

REM Get desktop path
for /f "tokens=3*" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set DESKTOP=%%b

REM Network path
set "NETWORK_PATH=\\Desktop-1\новая папка\code\debt-track"
set "VBS_FILE=%NETWORK_PATH%\launch_server_silent.vbs"
set "SHORTCUT=%DESKTOP%\Pharmacy Server.lnk"

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = 'wscript.exe'; $Shortcut.Arguments = '\"%VBS_FILE%\"'; $Shortcut.WorkingDirectory = '%NETWORK_PATH%'; $Shortcut.Description = 'Start Pharmacy Debt Tracker Server'; $Shortcut.WindowStyle = 7; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo.
    echo SUCCESS! Shortcut created on desktop.
    echo.
    echo The shortcut will:
    echo   - Start the server silently (no windows)
    echo   - Open the application in your browser
    echo   - Work completely in the background
    echo.
) else (
    echo.
    echo ERROR: Could not create shortcut.
    echo Please create it manually (see create_shortcut_manual.md)
    echo.
)

pause

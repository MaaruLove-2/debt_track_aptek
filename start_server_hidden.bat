@echo off
REM This script runs the server completely hidden (no window at all)

cd /d %~dp0

REM Create a VBS script to run the batch file hidden
echo Set WshShell = CreateObject("WScript.Shell") > _temp_hidden.vbs
echo WshShell.Run "cmd.exe /c python manage.py runserver 0.0.0.0:8000", 0, False >> _temp_hidden.vbs

REM Run the VBS script (which runs Python hidden)
cscript //nologo _temp_hidden.vbs

REM Clean up
timeout /t 2 /nobreak >nul
del _temp_hidden.vbs >nul 2>&1

REM Exit immediately (no window)
exit





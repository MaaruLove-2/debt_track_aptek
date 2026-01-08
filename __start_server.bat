@echo off 
cd /d "D:\shared\code\debt-track" 
echo Starting Django server... 
"D:\shared\code\debt-track\venv2\Scripts\python.exe" manage.py runserver 0.0.0.0:8000 
echo. 
echo Server stopped. Press any key to close... 
pause >nul 

@echo off
echo ========================================
echo   Pharmacy Website Server
echo ========================================
echo.
echo Starting server on all network interfaces...
echo Server will be accessible at: http://YOUR-IP:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo NOTE: To run in background (no window), use:
echo   - start_server_silent.vbs (for auto-start)
echo   - start_server_background.bat (for manual start)
echo ========================================
echo.

cd /d %~dp0
python manage.py runserver 0.0.0.0:8000

pause

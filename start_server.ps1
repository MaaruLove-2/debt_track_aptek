Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Pharmacy Website Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting server on all network interfaces..." -ForegroundColor Green
Write-Host "Server will be accessible at: http://YOUR-IP:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
python manage.py runserver 0.0.0.0:8000

Read-Host "Press Enter to exit"

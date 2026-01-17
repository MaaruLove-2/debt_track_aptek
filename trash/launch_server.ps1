# PowerShell script to launch Django server
$ErrorActionPreference = "Stop"

# Set the project directory (using the actual path found)
$projectDir = "D:\новая папка\code\debt-track"

# Change to project directory
Set-Location -LiteralPath $projectDir

Write-Host "========================================"
Write-Host "  Aptek Borc Izleyicisi"
Write-Host "  Starting Django Server..."
Write-Host "========================================"
Write-Host ""

# Check if virtual environment exists and use it
$venvPython = Join-Path $projectDir "venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "Using virtual environment..."
    $pythonCmd = $venvPython
} else {
    Write-Host "Using system Python..."
    $pythonCmd = "python"
    
    # Check if Django is installed
    try {
        $djangoCheck = & $pythonCmd -c "import django; print(django.get_version())" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Django not found. Installing dependencies..."
            & $pythonCmd -m pip install -r requirements.txt
        } else {
            Write-Host "Django $djangoCheck is installed"
        }
    } catch {
        Write-Host "Installing dependencies..."
        & $pythonCmd -m pip install -r requirements.txt
    }
}

# Start the server
Write-Host ""
Write-Host "Starting Django development server..."
Write-Host "Server will be available at: http://127.0.0.1:8000"
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

& $pythonCmd manage.py runserver








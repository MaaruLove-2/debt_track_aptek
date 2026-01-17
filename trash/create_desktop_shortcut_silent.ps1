# Script to create desktop shortcut for silent server launcher
# This creates a shortcut that runs without any windows

$ErrorActionPreference = "Stop"

Write-Host "========================================"
Write-Host "  Create Desktop Shortcut"
Write-Host "========================================"
Write-Host ""

# Get paths
$NetworkPath = "\\Desktop-1\новая папка\code\debt-track"
$VbsScript = Join-Path $NetworkPath "launch_server_silent.vbs"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Pharmacy Server.lnk"

# Check if VBS script exists
if (-not (Test-Path $VbsScript)) {
    Write-Host "ERROR: launch_server_silent.vbs not found!" -ForegroundColor Red
    Write-Host "Path: $VbsScript" -ForegroundColor Yellow
    pause
    exit 1
}

# Create shortcut
Write-Host "Creating desktop shortcut..." -ForegroundColor Cyan

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$VbsScript`""
$Shortcut.WorkingDirectory = $NetworkPath
$Shortcut.Description = "Start Pharmacy Debt Tracker Server"
$Shortcut.WindowStyle = 7  # Minimized (but won't show anyway with wscript)

# Try to set icon (optional - use Python icon if available)
try {
    $PythonPath = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($PythonPath) {
        $Shortcut.IconLocation = $PythonPath.Source + ",0"
    }
} catch {
    # Ignore icon errors
}

$Shortcut.Save()

Write-Host "✓ Shortcut created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Shortcut location: $ShortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "The shortcut will:" -ForegroundColor Yellow
Write-Host "  - Start the server silently (no windows)" -ForegroundColor White
Write-Host "  - Open the application in your browser" -ForegroundColor White
Write-Host "  - Work completely in the background" -ForegroundColor White
Write-Host ""
Write-Host "Just double-click the shortcut on your desktop!" -ForegroundColor Green
Write-Host ""
pause



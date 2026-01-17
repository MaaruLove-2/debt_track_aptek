# PowerShell script to create desktop shortcut for Django server
param(
    [string]$ProjectPath = $PSScriptRoot
)

# Hide PowerShell window
$windowStyle = 'Hidden'
if ($PSVersionTable.PSVersion.Major -ge 5) {
    Add-Type -Name Window -Namespace Console -MemberDefinition '
    [DllImport("Kernel32.dll")]
    public static extern IntPtr GetConsoleWindow();
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
    '
    $consolePtr = [Console.Window]::GetConsoleWindow()
    [Console.Window]::ShowWindow($consolePtr, 0) | Out-Null
}

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Aptek Borc İzləyicisi.lnk"
$VbsPath = Join-Path $ProjectPath "start_server.vbs"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $VbsPath
$Shortcut.WorkingDirectory = $ProjectPath
$Shortcut.Description = "Start Django development server and open Aptek Borc İzləyicisi"
$Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,13"
$Shortcut.Save()

# Show success message briefly
$wshell = New-Object -ComObject WScript.Shell
$wshell.Popup("Desktop shortcut created successfully!`n`nShortcut: Aptek Borc İzləyicisi", 3, "Success", 0x40)


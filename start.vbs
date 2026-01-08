' ==========================================
' Silent Django Launcher - Network Safe
' ==========================================

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' === CONFIGURATION ===
strNetworkPath = "D:\shared\code\debt-track"  ' Django project path
strServerIP = "192.168.100.11"                               ' Real IP to open in browser
strPort = "8000"                                             ' Django port
strVenv = "venv2"                                           ' Your virtual environment folder


' === If running, just open browser ===
' If serverRunning Then
'     objShell.Run "http://" & strServerIP & ":" & strPort, 1, False
'     WScript.Quit 0
' End If

' ' === Wait for network folder to be accessible ===
' ' Dim maxWait, waited
' ' maxWait = 10000   ' 10 seconds max
' ' waited = 0

' ' Do While waited < maxWait
' '     On Error Resume Next
' '     Set objFolder = objFSO.GetFolder(strNetworkPath)
' '     If Err.Number = 0 Then Exit Do
' '     WScript.Sleep 500
' '     waited = waited + 500
' '     On Error GoTo 0
' ' Loop

' ' If Err.Number <> 0 Then WScript.Quit 1

' ' === Change directory to project ===
' objShell.CurrentDirectory = strNetworkPath

' ' === Check if manage.py exists ===
' ' If Not objFSO.FileExists(strNetworkPath & "\manage.py") Then WScript.Quit 1

' === Locate Python executable from venv2 ===
Dim strPython
strPython = ""
If objFSO.FileExists(strNetworkPath & "\" & strVenv & "\Scripts\python.exe") Then
    strPython = strNetworkPath & "\" & strVenv & "\Scripts\python.exe"
Else
    WScript.Echo "Python not found in venv2."
    WScript.Quit 1
End If

' ' === Check if Django server is already running ===
' Dim serverRunning
' serverRunning = False

' Set objExec = objShell.Exec("netstat -an | findstr :" & strPort)
' Do While objExec.Status = 0
'     WScript.Sleep 100
' Loop
' If InStr(objExec.StdOut.ReadAll, strPort) > 0 Then
'     serverRunning = True
' End If

' === Start Django server silently ===
Dim strCommand
strCommand = """" & strPython & """ manage.py runserver 0.0.0.0:" & strPort
objShell.Run strCommand, 0, False

' ' === Wait for server to start (smart wait) ===
' Dim started, attempts
' started = False
' attempts = 0

' Do While started = False And attempts < 20   ' max 10 seconds (20 * 500ms)
'     Set objExec = objShell.Exec("netstat -an | findstr :" & strPort)
'     Do While objExec.Status = 0
'         WScript.Sleep 100
'     Loop
'     If InStr(objExec.StdOut.ReadAll, strPort) > 0 Then
'         started = True
'         Exit Do
'     End If
'     WScript.Sleep 500
'     attempts = attempts + 1
' Loop


' === Open browser to real IP ===
objShell.Run "http://" & strServerIP & ":" & strPort, 1, False
' === Exit silently ===
WScript.Quit 0

' Silent Django launcher (network-safe)

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strNetworkPath = "\\Desktop-1\shared\code\debt-track"
strServerIP = "192.168.100.11"

WScript.Sleep 2000

On Error Resume Next
Set objFolder = objFSO.GetFolder(strNetworkPath)
If Err.Number <> 0 Then WScript.Quit 1
On Error GoTo 0

objShell.CurrentDirectory = strNetworkPath

If Not objFSO.FileExists(strNetworkPath & "\manage.py") Then
    WScript.Quit 1
End If

' venv2 python
strPython = ""
If objFSO.FileExists(strNetworkPath & "\venv2\Scripts\python.exe") Then
    strPython = strNetworkPath & "\venv2\Scripts\python.exe"
End If

If strPython = "" Then WScript.Quit 1

' Check if already running
Set objExec = objShell.Exec("netstat -an | findstr :8000")
Do While objExec.Status = 0
    WScript.Sleep 100
Loop

If InStr(objExec.StdOut.ReadAll, "8000") > 0 Then
    objShell.Run "http://" & strServerIP & ":8000", 1, False
    WScript.Quit 0
End If

' Start Django
strCommand = """" & strPython & """ manage.py runserver 0.0.0.0:8000"
objShell.Run strCommand, 0, False

WScript.Sleep 1000

objShell.Run "http://" & strServerIP & ":8000", 1, False
WScript.Quit 0

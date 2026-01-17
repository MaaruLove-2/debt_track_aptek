Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' If script is on network path, use it directly; otherwise try to detect network path
If Left(strScriptPath, 2) = "\\" Then
    ' Already a network path
    objShell.CurrentDirectory = strScriptPath
Else
    ' Try network path
    strNetworkPath = "\\Desktop-1\новая папка\code\debt-track"
    If objFSO.FolderExists(strNetworkPath) Then
        strScriptPath = strNetworkPath
        objShell.CurrentDirectory = strScriptPath
    Else
        ' Use script directory
        objShell.CurrentDirectory = strScriptPath
    End If
End If

' Try to find Python executable
strPython = "python.exe"
strPythonW = "pythonw.exe"

' Check if pythonw.exe exists, if not use python.exe
On Error Resume Next
objShell.Run "where pythonw.exe", 0, True
If Err.Number <> 0 Then
    strPython = "python.exe"
Else
    strPython = "pythonw.exe"
End If
On Error GoTo 0

' Build the command
strCommand = strPython & " manage.py runserver 192.168.100.11:8000"

' Run the command in hidden window
objShell.Run strCommand, 0, False

' Log to file for debugging (optional)
Set objFile = objFSO.OpenTextFile(strScriptPath & "\server_log.txt", 8, True)
objFile.WriteLine Now & " - Server started with command: " & strCommand
objFile.Close

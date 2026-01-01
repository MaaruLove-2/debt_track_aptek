Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Change to the script directory
objShell.CurrentDirectory = strScriptPath

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
strCommand = strPython & " manage.py runserver 0.0.0.0:8000"

' Run the command in hidden window
objShell.Run strCommand, 0, False

' Log to file for debugging (optional)
Set objFile = objFSO.OpenTextFile(strScriptPath & "\server_log.txt", 8, True)
objFile.WriteLine Now & " - Server started with command: " & strCommand
objFile.Close

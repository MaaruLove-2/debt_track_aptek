Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Change to the script directory
objShell.CurrentDirectory = strScriptPath

' Try multiple Python paths
Dim arrPythonPaths
arrPythonPaths = Array( _
    "python.exe", _
    "pythonw.exe", _
    "py.exe", _
    "C:\Python310\python.exe", _
    "C:\Python311\python.exe", _
    "C:\Python312\python.exe", _
    "C:\Users\" & objShell.ExpandEnvironmentStrings("%USERNAME%") & "\AppData\Local\Programs\Python\Python310\python.exe", _
    "C:\Users\" & objShell.ExpandEnvironmentStrings("%USERNAME%") & "\AppData\Local\Programs\Python\Python311\python.exe", _
    "C:\Users\" & objShell.ExpandEnvironmentStrings("%USERNAME%") & "\AppData\Local\Programs\Python\Python312\python.exe" _
)

strPython = ""
For Each strPath In arrPythonPaths
    On Error Resume Next
    Set objExec = objShell.Exec("where " & strPath)
    objExec.StdOut.ReadAll
    If objExec.ExitCode = 0 Then
        strPython = strPath
        Exit For
    End If
    On Error GoTo 0
Next

' If Python not found, try direct execution
If strPython = "" Then
    strPython = "python.exe"
End If

' Build the command
strCommand = strPython & " manage.py runserver 0.0.0.0:8000"

' Create a batch file to run (more reliable)
strBatchFile = strScriptPath & "\_run_server_temp.bat"
Set objBatchFile = objFSO.CreateTextFile(strBatchFile, True)
objBatchFile.WriteLine "@echo off"
objBatchFile.WriteLine "cd /d """ & strScriptPath & """"
objBatchFile.WriteLine strCommand
objBatchFile.Close

' Run the batch file in hidden window
objShell.Run "cmd.exe /c """ & strBatchFile & """", 0, False

' Clean up batch file after a delay (optional)
WScript.Sleep 2000
On Error Resume Next
If objFSO.FileExists(strBatchFile) Then
    'objFSO.DeleteFile strBatchFile
End If
On Error GoTo 0



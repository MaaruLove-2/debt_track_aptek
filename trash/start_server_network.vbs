' VBScript to start Django server from network UNC path
' Works with: \\Desktop-1\новая папка\code\debt-track

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Network UNC path to project
strNetworkPath = "\\Desktop-1\новая папка\code\debt-track"

' Verify network path is accessible
On Error Resume Next
Set objFolder = objFSO.GetFolder(strNetworkPath)
If Err.Number <> 0 Then
    ' Network path not accessible, try to map or wait
    ' Log error
    Set objLogFile = objFSO.OpenTextFile(strNetworkPath & "\server_log.txt", 8, True)
    objLogFile.WriteLine Now & " - ERROR: Network path not accessible: " & strNetworkPath & " (Error: " & Err.Number & ")"
    objLogFile.Close
    
    ' Try again after a delay (network might not be ready at boot)
    WScript.Sleep 10000
    Set objFolder = objFSO.GetFolder(strNetworkPath)
    If Err.Number <> 0 Then
        ' Still failed, exit
        WScript.Quit 1
    End If
End If
On Error GoTo 0

' Change to network directory
objShell.CurrentDirectory = strNetworkPath

' Verify manage.py exists
If Not objFSO.FileExists(strNetworkPath & "\manage.py") Then
    Set objLogFile = objFSO.OpenTextFile(strNetworkPath & "\server_log.txt", 8, True)
    objLogFile.WriteLine Now & " - ERROR: manage.py not found in " & strNetworkPath
    objLogFile.Close
    WScript.Quit 1
End If

' Find Python executable
strPython = ""
arrPythonPaths = Array( _
    "python.exe", _
    "pythonw.exe", _
    "py.exe" _
)

For Each strPath In arrPythonPaths
    On Error Resume Next
    Set objExec = objShell.Exec("where " & strPath)
    Do While objExec.Status = 0
        WScript.Sleep 100
    Loop
    If objExec.ExitCode = 0 Then
        strPython = strPath
        Exit For
    End If
    On Error GoTo 0
Next

' If Python not found, try common locations
If strPython = "" Then
    strUsername = objShell.ExpandEnvironmentStrings("%USERNAME%")
    arrFullPaths = Array( _
        "C:\Python310\python.exe", _
        "C:\Python311\python.exe", _
        "C:\Python312\python.exe", _
        "C:\Python313\python.exe", _
        "C:\Python314\python.exe", _
        "C:\Users\" & strUsername & "\AppData\Local\Programs\Python\Python310\python.exe", _
        "C:\Users\" & strUsername & "\AppData\Local\Programs\Python\Python311\python.exe", _
        "C:\Users\" & strUsername & "\AppData\Local\Programs\Python\Python312\python.exe", _
        "C:\Users\" & strUsername & "\AppData\Local\Programs\Python\Python313\python.exe", _
        "C:\Users\" & strUsername & "\AppData\Local\Programs\Python\Python314\python.exe" _
    )
    
    For Each strFullPath In arrFullPaths
        If objFSO.FileExists(strFullPath) Then
            strPython = strFullPath
            Exit For
        End If
    Next
End If

' Default to pythonw.exe if still not found
If strPython = "" Then
    strPython = "pythonw.exe"
End If

' Check for virtual environment in network path
strVenvPython = strNetworkPath & "\venv\Scripts\python.exe"
If objFSO.FileExists(strVenvPython) Then
    strPython = strVenvPython
End If

' Build command - use 0.0.0.0 to listen on all interfaces
strCommand = """" & strPython & """ manage.py runserver 0.0.0.0:8000"

' Create a batch file on network path (more reliable for UNC paths)
strBatchFile = strNetworkPath & "\_start_server_network.bat"
Set objBatchFile = objFSO.CreateTextFile(strBatchFile, True)
objBatchFile.WriteLine "@echo off"
objBatchFile.WriteLine "cd /d """ & strNetworkPath & """"
objBatchFile.WriteLine strCommand
objBatchFile.Close

' Run the batch file in hidden window (0 = hidden)
objShell.Run "cmd.exe /c """ & strBatchFile & """", 0, False

' Log success
Set objLogFile = objFSO.OpenTextFile(strNetworkPath & "\server_log.txt", 8, True)
objLogFile.WriteLine Now & " - Server started from network path: " & strNetworkPath
objLogFile.WriteLine "  Command: " & strCommand
objLogFile.WriteLine "  Python: " & strPython
objLogFile.Close

' Clean up
Set objShell = Nothing
Set objFSO = Nothing


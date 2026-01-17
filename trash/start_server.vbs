Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

' Check if manage.py exists
If Not fso.FileExists(scriptDir & "\manage.py") Then
    MsgBox "ERROR: manage.py not found! Please make sure you're running this from the project directory.", vbCritical, "Aptek Borc İzləyicisi"
    WScript.Quit
End If

' Start Django server in completely hidden window (0 = hidden)
WshShell.Run "cmd /c python manage.py runserver", 0, False

' Wait for server to start
WScript.Sleep 4000

' Open browser to login page (1 = normal window)
WshShell.Run "http://127.0.0.1:8000/login/", 1, False

Set WshShell = Nothing
Set fso = Nothing


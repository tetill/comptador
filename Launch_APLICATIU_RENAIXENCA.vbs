Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this VBS file is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Set the working directory to the script's directory
WshShell.CurrentDirectory = scriptDir

' Try to run with pythonw first, then fallback to python
On Error Resume Next
WshShell.Run "pythonw APLICATIU_RENAIXENCA_15_OPTIMIZED.py", 0, False
If Err.Number <> 0 Then
    Err.Clear
    WshShell.Run "python APLICATIU_RENAIXENCA_15_OPTIMIZED.py", 1, False
    If Err.Number <> 0 Then
        MsgBox "Error: No s'ha pogut trobar Python. Assegura't que Python està instal·lat i accessible des del PATH del sistema.", vbCritical, "Error d'execució"
    End If
End If
On Error GoTo 0

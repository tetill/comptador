Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "n:\"
WshShell.Run "python APLICATIU_RENAIXENCA_15_OPTIMIZED.py", 0, False

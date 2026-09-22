Set WshShell = CreateObject("WScript.Shell")
' Run pythonw tray_app.py with 0 (hidden window mode)
WshShell.Run "pythonw tray_app.py", 0, False
Set WshShell = Nothing

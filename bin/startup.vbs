Dim objWShell
Set objWShell = WScript.CreateObject("WScript.Shell")
Set oWS = WScript.CreateObject("WScript.Shell")
appdata = objWShell.expandEnvironmentStrings("%APPDATA%")
sLinkFile = appdata + "\Microsoft\Windows\Start Menu\Programs\Startup\PrintConnector.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "C:\Program Files (x86)\Print Connector\PrintConnector.EXE"
    oLink.WorkingDirectory = "C:\Program Files (x86)\Print Connector"
oLink.Save
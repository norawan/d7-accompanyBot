import subprocess

def openFile(directory=None):
    winFileExplorer = 'Scripts/launchFileGUI.ps1'
    if directory == None:
        ps = subprocess.Popen(('powershell.exe', winFileExplorer), stdout=subprocess.PIPE)
    else:
        defaultPathArg = "-DefaultPath"
        assert(type(directory)==str)
        ps = subprocess.Popen(('powershell.exe', winFileExplorer, defaultPathArg, directory), stdout=subprocess.PIPE)
    ps.wait()
    return ps.stdout.read().decode().strip()
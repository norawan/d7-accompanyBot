import subprocess
import tkinter as tk
from tkinter import filedialog
from unzip import * # locally defined
import music21

# asks user input music score image file and desired output location for parsed xml
def loadMusic():
    root = tk.Tk()
    root.withdraw()

    print("Select input file")
    argString = filedialog.askopenfilename()
    print("Select output folder")
    outputString = filedialog.askdirectory()

    pathToAudiShell = "C:/Users/khand/OneDrive/Documents/GitHub/d7-accompanyBot/Scripts/runAudiveris.ps1"
    argStringName = "-argString"
    outputStringName = "-outputString"

    print("Reading sheet music...")
    readProc = subprocess.Popen(["powershell.exe", pathToAudiShell, argStringName, argString, outputStringName, outputString])
    readProc.wait()

    print("Unzipping binaries...")
    abstractFile = clearpath(argString).replace(".pdf", "").replace(".png", "") # better ways to do this
    newPath = outputString + f"/{abstractFile}/{abstractFile}.mxl"
    unzip(newPath, outputString)
    return f'{outputString}/{abstractFile}.xml'

# calls loadMusic and proceeds to play music read through the speaker
def readAndPlay():
    musicFile = loadMusic()
    musicStream = music21.converter.parse(musicFile)
    musicPlayer = music21.midi.realtime.StreamPlayer(musicStream)
    print(f"Now Playing: {musicFile}")
    musicPlayer.play()


readAndPlay()
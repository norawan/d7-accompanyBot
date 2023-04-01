from gpio import *
from music21 import *
from xml_parse import *
from macros import *

import time
import serial

def mapNotes(startingNote):
    """Maps the note:pin noteToPinDict dictionary based on the starting note.
       Starting note must be a white key
    
    Args: startingNote (String): the note that the octave starts at
    """
    startIndex = startingNoteToOffset.get(startingNote, "ERROR")
    if (startIndex == "ERROR"):
        print("Does not start on a white key")
        return
    
    for element in noteToPinIndex:
        print(element)
        elementIndex = noteToPinIndex[element]
        print(elementIndex)

def isNoteInRange(note, octave):
    return True

def playNotes(setOfNotes, currentOctave):
    """Plays the notes in a list of notes
    
    Args: currentMeasure (int): The time step to retreive notes for
    """
    # print(bin(pi.read_bank_1())) # For debugging
    for note in setOfNotes:
        pitch = note.pitch
        octave = note.octave
        state = note.state
        
        pin = noteToPinDict.get(pitch, "NO PIN")
        if (pin == "NO PIN"):
            print("Error: Not a valid pitch\n")
        elif (not isNoteInRange(note, octave)):
            print("Note outside of current octave\n")
        else:
            # Note is playable
            if (state):
                if (len(currentlyPlaying) == 5):
                    break
                currentlyPlaying.add(pitch)
            else:
                if (pitch in currentlyPlaying):
                    currentlyPlaying.remove(pitch)
            pi.write(pin, state)
    
    # print(currentlyPlaying)

def getMeasureFromTime():
    currentTime = time.time_ns()
    elapsedTime = currentTime - startTime
    measureNumber = elapsedTime // measureDuration + startMeasure
    return measureNumber

def getCurrentOffset():
    currentTime = time.time_ns()
    elapsedTime = currentTime - startTime
    offset = (elapsedTime / measureDuration) - currentMeasure + startMeasure
    return offset

def checkSerialInput():
    if (ser.inWaiting() == 0):
        
        return 0
    else:
        buf = ser.readline()
        print(buf)
        return 1
# Set up hardware
ser = serial.Serial('/dev/serial0', 115200, timeout=1)

pi = setUpPins()

# Initializing variables

startTime = time.time_ns()
startMeasure = 1
currentMeasure = 1
justStarted = 1
currentOffset = 0
currentOctave = 3
notesToPlay = {}
currentlyPlaying = set()
offsetList = []
paused = 0

# Run scheduling

scheduledPiece = dict()
(measureDuration, totalMeasures, scheduledPiece) = schedule("MetronomeTest120bpm.xml", scheduledPiece)
print(scheduledPiece)

mapNotes("C")

# Golden Loop
while(True):
    command = checkSerialInput()
    if (command != 0):
        print("here!\n")
        ser.write(b"received\n")
        #startMeasure = 0 # parse from command?
        #startTime = time.time()
        #justStarted = 1
        #currentMeasure = startMeasure - 1
        #currentOffset = 0
        #notesToPlay = {}
        #currentlyPlaying = {}
        #offsetList = []
        #paused = 0

    elif (command == 0):
        newMeasure = getMeasureFromTime()
        if (justStarted or newMeasure > currentMeasure):
            # print(newMeasure)
            justStarted = 0
            currentMeasure = newMeasure
            notesToPlay = scheduledPiece.get(currentMeasure, "none")
            if (notesToPlay != "none"):
                offsetList = list(notesToPlay.keys())
                offsetList.sort()
        
        newOffset = getCurrentOffset()
        if (len(offsetList) > 0 and newOffset > offsetList[0]):
            # print(".")
            # print(offsetList[0])
            if (notesToPlay != "none"):
                notesAtOffset = notesToPlay.get(offsetList[0], "none")
            if (notesAtOffset != "none"):
                playNotes(notesAtOffset, currentOctave)
            offsetList = offsetList[1:]
    else:
        pass

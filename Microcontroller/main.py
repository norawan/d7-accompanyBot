from gpio import *
from music21 import *
from xml_parse import *
from macros import *

import time
import sys
import serial

DEBUG = True
RPI_CONNECTED = True

def isNoteInRange(note, octave):
    return True

def playNotes(setOfNotes, currentOctave):
    """Plays the notes in a list of notes
    
    Args: currentMeasure (int): The time step to retreive notes for
    """
    for note in setOfNotes:
        pitch = note.pitch
        octave = note.octave
        state = note.state
        
        pin = noteToPinDict.get(pitch, "NO PIN")
        if (pin == "NO PIN"):
            print("ERROR: Not a valid pitch\n")
        elif (not isNoteInRange(note, octave)):
            print("Note outside of current octave\n")
        else:
            # Note is playable
            if (state):
                if (len(currentlyPlaying) == 5):
                    break
                currentlyPlaying.add(pitch)
                if (DEBUG): print(".")
            else:
                if (pitch in currentlyPlaying):
                    currentlyPlaying.remove(pitch)
            if (RPI_CONNECTED): pi.write(pin, state)
    
    if (DEBUG): print(currentlyPlaying)
    
def stopPlaying():
    if (RPI_CONNECTED): pi.clear_bank_1(POSSIBLE_PINS)

def getMeasureFromTime():
    currentTime = time.time_ns()
    elapsedTime = currentTime - startTime
    measureNumber = elapsedTime // measureDuration_ns + (startMeasure)
    return measureNumber

def getCurrentOffset():
    currentTime = time.time_ns()
    elapsedTime = currentTime - startTime
    offset = (elapsedTime / measureDuration_ns) - currentMeasure + startMeasure
    return offset

def checkSerialInput():
    if (RPI_CONNECTED):
        if (ser.inWaiting() == 0):
            return
        else:
            buf = ser.readline()
            if (DEBUG): print(buf)
            return buf.decode()

# Set up hardware
if (RPI_CONNECTED): ser = serial.Serial('/dev/serial0', 115200, timeout=10)

if (RPI_CONNECTED): pi = setUpPins()

# Initializing variables

startTime = time.time_ns()
startMeasure = 1
currentMeasure = 2
totalMeasures = 0
justStarted = True
currentOffset = 0
currentOctave = 3
notesToPlay = {}
currentlyPlaying = set()
offsetList = []
paused = True

# Run scheduling
scheduledPiece = dict()
(tempoInfo, totalMeasures, scheduledPiece) = schedule("MetronomeTest120bpm.xml", scheduledPiece)
measureDuration_ns = tempoInfo.getMeasureDuration_ns()
if (DEBUG): print(scheduledPiece)

startTime = time.time_ns()

# Golden Loop
while(True):
    command = checkSerialInput()
    if (command != None):
        # Set Parameters based on received command

        # Play 
        if (command[0] == "S"):
            if (DEBUG): print("Start Playing")
            paused = False
            justStarted = True
            startTime = time.time_ns()

        # Pause   
        elif (command[0] == "P"):
            if (DEBUG): print("Pause Playing")
            stopPlaying()
            paused = True
        
        # Change the current measure
        elif (command[0] == "C"):
            measure = command[1:-1] # Removes the new line character
            
            if (DEBUG): print("Parsed measure: " + measure)
            
            startMeasure = int(measure)
            currentMeasure = startMeasure
            justStarted = True
            startTime = time.time_ns()

        # New Tempo Received
        elif (command[0] == "T"):
            newTempo = command[1:-1] # Removes the new line character

            if (DEBUG): print("New Tempo: " + newTempo)

            tempoInfo.tempoValue = newTempo
            measureDuration_ns = tempoInfo.getMeasureDuration_ns()
            startMeasure = currentMeasure
            startTime = time.time_ns()

        # File received
        elif (command[0] == "F"): 
            file = command[1:-1] # Removes the new line character
            
            # Check that file exists
            try: 
                open(file)
            except: 
                print("ERROR: File not found")
                # Tell computer that file upload failed
                break

            (tempoInfo, totalMeasures, scheduledPiece) = schedule(file, scheduledPiece)
            measureDuration_ns = tempoInfo.getMeasureDuration_ns()

            # Initialize variables for the new song
            startMeasure = 1
            currentMeasure = 1
            currentOffset = 0
            notesToPlay = {}
            currentlyPlaying = set()
            offsetList = []
            paused = True

    else:
        if (not paused and currentMeasure <= totalMeasures):
            newMeasure = getMeasureFromTime()
            if (justStarted or newMeasure > currentMeasure):
                if (DEBUG): print("Measure: {}".format(newMeasure))
                
                justStarted = 0
                currentMeasure = newMeasure
                notesToPlay = scheduledPiece.get(currentMeasure, "none")
                if (notesToPlay != "none"):
                    offsetList = list(notesToPlay.keys())
                    offsetList.sort()
                
                # Send new measure number over serial port to computer
                writeData = "C" + str(currentMeasure) + "\n"
                if (RPI_CONNECTED): ser.write(writeData.encode())
            
            newOffset = getCurrentOffset()
            # print("offset" + str(newOffset))
            if (len(offsetList) > 0 and newOffset > offsetList[0]):
                # print(offsetList[0])
                if (notesToPlay != "none"):
                    notesAtOffset = notesToPlay.get(offsetList[0], "none")
                if (notesAtOffset != "none"):
                    playNotes(notesAtOffset, currentOctave)
                offsetList = offsetList[1:]
        else:
            pass

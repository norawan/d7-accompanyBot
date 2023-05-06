from gpio import *
from music21 import *
from xml_parse import *
from pin_mapping import *

import time
import os
import serial

# Macros
DEBUG = True
RPI_CONNECTED = True
RPI_SER_PORT = '/dev/serial0'
DEFAULT_BAUD = 115200
MAX_LATENCY = 10 # in seconds
XML_FILES_PATH = "/home/pi/d7-accompanyBot/XMLFiles/"
DEFAULT_OCTAVE = 3
MAX_NOTES = 5

def isNoteInRange(octave):
    return (octave == currentOctave)

def playNotes(setOfNotes, currentOctave):
    """Plays the notes in a list of notes

    Args: currentMeasure (int): The time step to retreive notes for
    """
    print(setOfNotes)
    for note in setOfNotes:
        pitch = note.pitch
        octave = note.octave
        state = note.state
        print(pitch)

        pin = noteToPinDict.get(pitch, "NO PIN")
        if (pin == "NO PIN"):
            print("ERROR: Not a valid pitch\n")
        elif (not isNoteInRange(octave)):
            print("Note outside of current octave\n")
        else:
            # Note is playable
            if (state):
                if (len(currentlyPlaying) == MAX_NOTES):
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
    print(bin(pi.read_bank_1() & POSSIBLE_PINS))

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
    if (not RPI_CONNECTED): return None
    if (ser.inWaiting() == 0):
        return None
    else:
        buf = ser.readline()
        print(buf)
        command = buf.decode()
        print(command)
        return command[:-1] # Remove new line character

# Set up hardware
ser = serial.Serial(RPI_SER_PORT, DEFAULT_BAUD, timeout=MAX_LATENCY)

pi = setUpPins()

pi.clear_bank_1(POSSIBLE_PINS)

# Initializing variables
scheduledPiece = dict()
startTime = time.time_ns()
startMeasure = 1
currentMeasure = 1
totalMeasures = 0
justStarted = True
currentOffset = 0
currentOctave = DEFAULT_OCTAVE
notesToPlay = {}
currentlyPlaying = set()
offsetList = []
paused = True
fileLoaded = False
measureDuration_ns = 0

# Run scheduling
#(tempoInfo, totalMeasures, scheduledPiece, currentOctave) = schedule("/home/pi/d7-accompanyBot/XMLFiles/ChromaticCscale.xml", scheduledPiece)
#if (tempoInfo.tempoValue > tempoInfo.maxTempo):
#    print(f"ERROR: Parsed tempo of {tempoInfo.tempoValue} exceeds max tempo. Playing with max tempo of {tempoInfo.maxTempo}")
#    tempoInfo.tempoValue = tempoInfo.maxTempo
#fileLoaded = True

#measureDuration_ns = tempoInfo.getMeasureDuration_ns()
#if (DEBUG): print(scheduledPiece)

print("Starting loop")

# Golden Loop
while(True):
    # try and except to catch errors
    try:
        command = checkSerialInput()
        if (command != None):
            # Set Parameters based on received command

            # Play
            if (command == "S"):
                if (DEBUG): print("Start Playing")

                if (paused and fileLoaded):
                    paused = False
                    justStarted = True
                    startMeasure = currentMeasure
                    startTime = time.time_ns()

                    print("received start")

            # Pause
            elif (command == "P"):
                if (fileLoaded):
                    if (DEBUG): print("Pause Playing")
                    stopPlaying()
                    paused = True

                print("received pause")

            # Change the current measure
            elif (command[0] == "C" and len(command) > 1):
                if (fileLoaded):
                    measure = command[1:] # Removes the first character

                    if (DEBUG): print("Parsed measure: " + measure)

                    startMeasure = int(measure)
                    currentMeasure = startMeasure
                    justStarted = True
                    startTime = time.time_ns()

            # New Tempo Received
            elif (command[0] == "T" and len(command) > 1):
                if (fileLoaded):
                    newTempo = int(command[1:]) # Removes the first character

                    if (DEBUG): print("New Tempo: " + str(newTempo))

                    if (newTempo > tempoInfo.maxTempo):
                        print(f"ERROR: Input tempo of {newTempo} too high. Using max tempo of {tempoInfo.maxTempo} instead")
                    tempoInfo.tempoValue = min(tempoInfo.maxTempo, newTempo)

                    # Recalculate measure duration and set time variables
                    measureDuration_ns = tempoInfo.getMeasureDuration_ns()
                    startMeasure = currentMeasure
                    startTime = time.time_ns()

            # File received
            elif (command[0] == "F"  and len(command) > 1):
                file = command[1:] # Removes the first character

                filepath = XML_FILES_PATH + file

                print(filepath)

                # Check that file exists
                try:
                    open(filepath) # To catch the exception for if the file doesn't exist
                    fileLoaded = True
                    newScheduledPiece = dict()
                    (tempoInfo, totalMeasures, newScheduledPiece, currentOctave) = schedule(filepath, scheduledPiece)

                    # Check that tempo is not too high
                    print("Max Tempo: " + str(tempoInfo.maxTempo))
                    if (tempoInfo.tempoValue > tempoInfo.maxTempo):
                        print(f"ERROR: Parsed tempo of {tempoInfo.tempoValue} exceeds max tempo. Playing with max tempo of {tempoInfo.maxTempo}")
                        tempoInfo.tempoValue = tempoInfo.maxTempo

                    ser.write(("N" + str(totalMeasures) + "\n").encode())
                    ser.write(("M" + str(tempoInfo.maxTempo) + "\n").encode())
                    ser.write(("O" + str(currentOctave) + "\n").encode())
                    ser.write(("C0\n").encode())

                    scheduledPiece = newScheduledPiece
                    measureDuration_ns = tempoInfo.getMeasureDuration_ns()

                    # Initialize variables for the new song
                    startMeasure = 1
                    currentMeasure = 1
                    currentOffset = 0
                    notesToPlay = {}
                    currentlyPlaying = set()
                    offsetList = []
                    paused = True
                except:
                    print("ERROR: File not found")
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
    except:
        pass

# Should never reach here
print("Program terminated")
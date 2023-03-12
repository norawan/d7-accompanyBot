from gpio import *
from music21 import *
from xml_parse import *
from macros import *

import time

def playCurrentTimeNotes(curentTime):
    """Gets the bit mask for the input time from the notesToPlay dict and sends it to the GPIO pins
    
    Args: currentTime (int): The time step to retreive notes for
    """
    bitBank = notesToPlay.get(currentTime, "ERROR")
    if (bitBank != "ERROR"):
        #print(bin(bitBank))
        pi.set_bank_1(bitBank)
        clearBank = (~bitBank & POSSIBLE_PINS)
        #print(bin(clearBank))
        pi.clear_bank_1(clearBank)

def liftCurrentTimeNotes(currentTime):
    """Gets the pins of the notes that need to be lifted

    Args: currentTime (int): The time step to retreive lifted notes for
    """
    liftList = notesToPlay.get(currentTime, "ERROR")
    if (liftList != "ERROR"):
        for liftedNote in liftList:
            pi.write(liftedNote, 0)

smallestNote = 16 # i.e. 16th note

notesToPlay = dict()
notesToLift = dict()
(timeDelay, notesToPlay) = schedule(smallestNote, notesToPlay, notesToLift)
print(notesToPlay)
print(notesToLift)

pi = setUpPins()

currentTime = 0
timeDelay = timeDelay/1000

# Executes the tasks for a time and updates the time. Then waits for the duration of the delay interval
# Eventually will include receiving from serial input connected to laptop
while(True):
    liftCurrentTimeNotes(currentTime)
    playCurrentTimeNotes(currentTime)
    currentTime += 1
    #print(bin(pi.read_bank_1())) # For debugging
    time.sleep(timeDelay)

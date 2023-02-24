from gpio import *
from music21 import *
import time

# Macros
POSSIBLE_PINS = 0xC432E6C

# Global Variables
notesToPlay = dict()
currentTime = 0
delayInterval = 0
beatType = 4
smallestNote = 8 # i.e. 8th note

# Sample Sequence
notesToPlay[0] = POSSIBLE_PINS
notesToPlay[1] = notesToPlay[0] & ~PIN0_MASK 
notesToPlay[2] = notesToPlay[1] & ~PIN1_MASK 
notesToPlay[3] = notesToPlay[2] & ~PIN2_MASK 
notesToPlay[4] = notesToPlay[3] & ~PIN3_MASK 
notesToPlay[5] = notesToPlay[4] & ~PIN4_MASK 
notesToPlay[6] = notesToPlay[5] & ~PIN5_MASK 
notesToPlay[7] = notesToPlay[6] & ~PIN6_MASK 
notesToPlay[8] = notesToPlay[7] & ~PIN7_MASK 
notesToPlay[9] = notesToPlay[8] & ~PIN8_MASK 
notesToPlay[10] = notesToPlay[9] & ~PIN9_MASK 
notesToPlay[11] = notesToPlay[10] & ~PIN10_MASK 
notesToPlay[12] = notesToPlay[11] & ~PIN11_MASK 
notesToPlay[13] = notesToPlay[12] & ~PIN12_MASK 

# Convert an array of Bools to the corresponding bit mask bank
def getBitMaskFromKeyArr(arr):
    bitMask
    if(arr[0]):
        bitMask |= PIN0
    # Not finished yet. Is there a better way to do this then just if/elif/else?

# Initialize global variables used for timing and scheduling 
def initScheduler(tempo):
    noteDuration = (600000/tempo) * beatType # in miliseconds
    delayInterval = noteDuration/smallestNote
    # Tempory values. Will be used in scheduling


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

# Executes the tasks for a time and updates the time. Then waits for the duration of the delay interval
# Eventually will include receiving from serial input connected to laptop
while(True):
    playCurrentTimeNotes(currentTime)
    currentTime += 1
    #print(bin(pi.read_bank_1())) # For debugging
    time.sleep(0.05)

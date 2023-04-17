# Latency test - to be run on the computer

import time
import serial

def isValidCommand(input):
    if (not isinstance(input, str)):
        return False
    if (input[0] == "S"):
        return True
    elif (input[0] == "P"):
        return True
    elif (input[0] == "C"):
        if (int(input[1:]) >= 0):
            return True
        else: 
            return False
    elif (input[0] == "F"):
        return True
    elif (input[0] == "T"):
        if (int(input[1:]) >= 0):
            return True
        else: 
            return False
    else: 
        return False

# Serial communication parameters
port = '/dev/tty.usbmodem2101'
baudrate = 115200
timeoutTime = 1

ser = serial.Serial(port, baudrate, timeout=timeoutTime)

if (ser.is_open):

    while (True):
        inp = input("Type a command: ")
        inp = inp + "\n"
        print(inp.encode())
        if (isValidCommand(inp)):
            ser.write(inp.encode())
else:
    print("Failed to open serial port\n")



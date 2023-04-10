# Test sending a file - to be run on the computer

import time
import serial

# Serial communication parameters
port = '/dev/tty.usbmodem2101'
baudrate = 115200
timeoutTime = 1

ser = serial.Serial(port, baudrate, timeout=timeoutTime)

if (ser.is_open):
    startTime = time.time_ns()

    file = open("Charlie_Brown_Theme.xml", "r")
    dataToWrite = file.read()
    
    print(dataToWrite)
    ser.write(dataToWrite.encode())
    ser.write(b"EOF\n")

    while (ser.in_waiting == 0):
        pass

    string = ser.readline()
    print(string.decode())

    endTime = time.time_ns()

    latency_ms = (endTime - startTime) / 1000000
    print(f"Latency in miliseconds: {latency_ms}\n")
else:
    print("Failed to open serial port\n")
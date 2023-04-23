import serial
from constants import *
import copy
import serial.tools.list_ports
import os

def sendFileToRPi(xmlfile):
    fullcommand = "scp " + xmlfile + " " + RPI_SCP_ADDR + ":" + RPI_MUSIC_DIR
    print(fullcommand)
    os.system("scp -o ConnectTimeout=1 " + xmlfile + " " + RPI_SCP_ADDR + ":" + RPI_MUSIC_DIR)
    return

def connectToCommPort():
    serialPort = None
    comports = serial.tools.list_ports.comports()
    for port in comports:
        print(port.description)
        desc = port.description
        if (ARDUINO_PORT in desc or ARDUINO_PORT_ALT in desc) and BAD_PORT not in port.description:
            try:
                serialPort = serial.Serial(port.name, baudrate=DEFAULT_BAUD, timeout=COMM_TIMEOUT)
                print("Connected to player device!")
                return serialPort
            except:
                print("Device located but could not connect")
                return None
    print("Failed to locate device")
    return None


def communicateSend(toSend : dict, commPort : serial.Serial):
    while True:
        if KILL_COMMAND in toSend:
            return
        
        sendCopy = copy.copy(toSend)
        for key in sendCopy:
            if key == KILL_COMMAND:
                continue   

            value = sendCopy[key]
            rv = 0
            if key == PLAY_COMMAND or key == PAUSE_COMMAND:
                print("sent pause/play")
                rv = commPort.write(key.encode())
            elif key == MEASURE_COMMAND or key == SEND_FILE:
                if key == SEND_FILE:
                    print("sent F command")
                rv = commPort.write(value.encode())
            
            if rv > 0:
                try:
                    toSend.pop(key)
                except:
                    pass
    
    
def communicateReceive(toReceive : dict, commPort : serial.Serial):
    while True:
        if KILL_COMMAND in toReceive:
            return
        else:
            data = commPort.readline().decode().strip()
            if len(data) > 0:
                if data[0] == "C":
                    measureNumber = int(data[1:])
                    toReceive[MEASURE_COMMAND] = measureNumber
                elif data[0] == "T":
                    tempoNumber = int(data[1:])
                    toReceive[TEMPO_COMMAND] = tempoNumber
                elif data[0] == "N":
                    measureCount = int(data[1:])
                    toReceive[COUNT_COMMAND] = measureCount
                elif data[0] == "O":
                    octaveNumber = int(data[1:])
                    toReceive[OCTAVE_COMMAND] = octaveNumber
                elif data[0] == "L":
                    latencyNumber = int(data[1:])
                    toReceive[LATENCY_TEST] = latencyNumber
                



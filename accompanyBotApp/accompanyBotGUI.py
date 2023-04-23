import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # remove self-advertisement

from constants import *
from procedures import *
from fileOpener import openFile
from threading import Thread
from communicate import *
import time
import copy
import music21

class ThreadReturn(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
    
    
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((972, 700), 
                                DESIRED_EFFECTS)

pygame.display.set_caption('accompanyBot')
iconAttribution = '<a href="https://www.flaticon.com/free-icons/piano" title="piano icons">Piano icons created by Freepik - Flaticon</a>'
# icon taken from flaticon.com
iconImage = pygame.image.load("accompanyBotApp/piano.png")
pygame.display.set_icon(iconImage)

running = True

# application objects
objects = createObjects(screen)
colors = createColors()
radii = createRadii(screen)
showing = createShowParams(objects)
explorerThread = ThreadReturn(None)
explorerStarted = False
omrThread = ThreadReturn(None)
toSend = dict()
toReceive = dict()
commPort = None
senderThread = Thread(None)
receiverThread = Thread(None)
omrStarted = False
musicScoreFile = ""
musicPages=[]
device = "None"
numMeasures = 0
curMeasure = 0
userHasOrb=False
extraThreadAlert=dict()
extraThreadAlert[KILL_COMMAND] = False
extraThreadAlert[CURRENT_XML] = ""
orbPos=(ORBX, ORBY)
tempo=100
oldKeyPressTime=0
newKeyPressTime=0
digitalDemo = False
newSong = False
displaySetup = True
octaveNum = 0
startedLatency = 0
endedLatency = 0
debug = False
drawMusicFlag = False


while running:
    keysPressed = pygame.key.get_pressed()
    mouseX, mouseY = pygame.mouse.get_pos()
    
    if omrStarted and not omrThread.is_alive(): # OMR finished processing
        omrOutput = omrThread.join()
        if omrOutput is None:
            print("Audiveris failed to process music score input")
            drawMusicFlag = False
        else:
            print("breaking: " + musicScoreFile)
            musicPages = breakPages(musicScoreFile) # wrapper for png vs pdf files
            drawMusicFlag = True
            try:
                '''xmlfile = open(omrOutput, 'r')
                xmlString = xmlfile.read()
                goodXml = xmlString.split("measure number=\"")
                maxMeasure = 0
                for xmlPiece in goodXml[1:]:
                    number = int(xmlPiece.split('\"')[0])
                    if number > maxMeasure:
                        maxMeasure = number

                numMeasures = maxMeasure
                xmlfile.close()'''

                # correct voicings
                # xmlfile = open(omrOutput, 'w+r')
                # xmlString = xmlfile.read()
                # fixedXmlString = xmlString.replace(PART_VOICE, PART_PIANO) \
                #     .replace(INSTRUMENT_VOICE, INSTRUMENT_PIANO) \
                #     .replace(MIDI_PROGRAM_VOICE, MIDI_PROGRAM_PIANO)
                # xmlfile.write(fixedXmlString)
                # xmlfile.close()
            except:
                print("Error while loading measure count or updating file")

            try: # load digital player
                converter = music21.converter.parse(omrOutput)
                converter.write(fmt="midi", fp=MIDI_STRING)
                pygame.mixer.music.load(MIDI_STRING)
                newSong = True
                digitalDemo = True
            except:
                print("Error while loading digital player")

            
            sendFileToRPi(omrOutput)
            toSend[SEND_FILE] = "F" + clearpath(omrOutput) + "\n"
            
        omrStarted = not omrStarted

    if explorerStarted and not explorerThread.is_alive(): # file chosen or canceled
        musicScoreFile = (explorerThread.join()).replace("\\", "/", -1)
        explorerStarted = not explorerStarted

        if musicScoreFile == "": # Cancelled
            pass
        else: # file chosen
            if len(musicScoreFile) < 4 or (musicScoreFile[-4:] != ".png" and musicScoreFile[-4:] != ".pdf"):
                print("Please insert a png or pdf file")
            elif omrStarted:
                print("Please wait for previous upload to finish processing")
            else:
                omrThread=ThreadReturn(target=processMusic, args=(musicScoreFile, AUDIVERIS_OUTPUT_LOCATION, extraThreadAlert,))
                omrThread.start()
                omrStarted = True
                drawMusicFlag = False
                pygame.mixer.music.stop()

    receivedStuff = copy.copy(toReceive)
    for command in receivedStuff: # write receiving buffer information here
        commValue = toReceive[command]
        if command == KILL_COMMAND:
            continue
        elif command == MEASURE_COMMAND:
            curMeasure = commValue
        elif command == TEMPO_COMMAND:
            tempo = commValue
        elif command == COUNT_COMMAND:
            numMeasures = commValue
        elif command == OCTAVE_COMMAND:
            displaySetup = True
            octaveNum = commValue
        elif command == LATENCY_TEST:
            latencyNum = commValue
            endedLatency = time.time_ns()
            if debug: print("Received " + str(latencyNum) + f" after {endedLatency - startedLatency} ns")
            
        try:
            toReceive.pop(command)
        except:
            pass
        
 
    curMeasure = updateCurrentMeasure(screen, userHasOrb, curMeasure, numMeasures, mouseX) # update current measure with mouse
    orbPos = updateMeasureOrb(curMeasure, numMeasures, orbPos) # match orb position to current measure
    if userHasOrb:
        addMeasureForSend(toSend, curMeasure)

    objects[16] = orbOnScreen(screen, orbPos)  # update slider graphics
    objects[17] = createTempoText(screen, tempo) # update tempo graphics
    objects[21] = createMeasureNumText(screen, curMeasure) # update measure number graphics

    if keysPressed[K_UP]:
        newKeyPressTime = time.time_ns()
        if newKeyPressTime > (oldKeyPressTime + INPUT_BUFFER):
            tempo = increaseTempo(tempo) # TODO set threshold
            oldKeyPressTime = newKeyPressTime
    elif keysPressed[K_DOWN]:
        newKeyPressTime = time.time_ns()
        if newKeyPressTime > (oldKeyPressTime + INPUT_BUFFER):
            tempo = decreaseTempo(tempo) # TODO set threshold
            oldKeyPressTime = newKeyPressTime
    elif keysPressed[K_LEFT]:
        newKeyPressTime = time.time_ns()
        if newKeyPressTime > (oldKeyPressTime + INPUT_BUFFER):
            curMeasure = goPrevMeasure(curMeasure)
            addMeasureForSend(toSend, curMeasure)
            oldKeyPressTime = newKeyPressTime
    elif keysPressed[K_RIGHT]:
        newKeyPressTime = time.time_ns()
        if newKeyPressTime > (oldKeyPressTime + INPUT_BUFFER):
            curMeasure = goNextMeasure(curMeasure, numMeasures)
            addMeasureForSend(toSend, curMeasure)
            oldKeyPressTime = newKeyPressTime

    for event in pygame.event.get(): # event loop
        if event.type == QUIT: # quit and close threads
            running = False
            toReceive[KILL_COMMAND] = True
            toSend[KILL_COMMAND] = True
            extraThreadAlert[KILL_COMMAND] = True
        elif event.type == KEYDOWN:
            if event.key == K_SPACE and digitalDemo:
                if newSong:
                    pygame.mixer.music.play(-1)
                    newSong = False
                elif pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
        elif event.type == KEYUP:
            pass
        elif event.type == VIDEORESIZE:
            width, height = event.size
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                width = MIN_WIDTH
                height = MIN_HEIGHT
            screen = pygame.display.set_mode((width, height), DESIRED_EFFECTS)
            objects = createObjects(screen, device, orbPos, tempo, curMeasure)
            radii = createRadii(screen)
        elif event.type == MOUSEBUTTONDOWN:
            if displaySetup:
                displaySetup = False
            elif showing[22] and mouseInButton(objects[22], mouseX, mouseY):
                extraThreadAlert[CACHE_REQUEST] = EXISTING_FILE
            elif showing[23] and mouseInButton(objects[23], mouseX, mouseY):
                extraThreadAlert[CACHE_REQUEST] = REPROCESS_FILE
            elif mouseInButton(objects[0], mouseX, mouseY): # pdf/png button click
                if not explorerThread.is_alive() and not omrStarted:
                    explorerThread = ThreadReturn(target=openFile, args=(extraThreadAlert,))
                    explorerStarted = True
                    explorerThread.start()
            elif mouseInButton(objects[1], mouseX, mouseY):
                commPort = connectToCommPort() # TODO implement device connection logic
                if commPort is not None:
                    receiverThread = Thread(target=communicateReceive, args=(toReceive, commPort))
                    senderThread = Thread(target=communicateSend, args=(toSend, commPort))
                    receiverThread.start()
                    senderThread.start()
                    device = "accompanyBot v1"
                else:
                    device = "None"
                objects = createObjects(screen, device, orbPos, tempo, curMeasure)
            elif mouseInTriangle(objects[9], mouseX, mouseY): # increase tempo
                tempo = increaseTempo(tempo) # TODO add threshold parameter
            elif mouseInTriangle(objects[10], mouseX, mouseY): # decrease tempo
                tempo = decreaseTempo(tempo)
            elif showing[11] and mouseInTriangle(objects[11], mouseX, mouseY): # play
                toSend[PLAY_COMMAND] = True
                if PAUSE_COMMAND in toSend: toSend.pop(PAUSE_COMMAND)
                showing[11] = not showing[11]
                showing[18] = not showing[18]
                showing[19] = not showing[19]
                startedLatency = time.time_ns()
            elif (not showing[11]) and mouseInPauseButton(objects[18], objects[19], mouseX, mouseY): # pause
                toSend[PAUSE_COMMAND] = True
                if PLAY_COMMAND in toSend:  toSend.pop(PLAY_COMMAND)
                showing[11] = not showing[11]
                showing[18] = not showing[18]
                showing[19] = not showing[19]
                startedLatency = time.time_ns()
            elif mouseInTriangle(objects[12], mouseX, mouseY): # next measure
                curMeasure = goNextMeasure(curMeasure, numMeasures)
                addMeasureForSend(toSend, curMeasure)
            elif mouseInTriangle(objects[13], mouseX, mouseY): # prev measure
                curMeasure = goPrevMeasure(curMeasure)
                addMeasureForSend(toSend, curMeasure)
            elif mouseInCircle(objects[16], radii[16], mouseX, mouseY): # clicking in slider
                userHasOrb = True
            pass
        elif event.type == MOUSEBUTTONUP:
            userHasOrb = False


    screen.fill(BACKGROUND)
    drawCacheMessage(extraThreadAlert, screen, showing)
    drawObjects(screen, objects, colors, radii, showing)
    drawMusic(screen, musicPages, drawMusicFlag) # TODO incorporate some indicator to determine page flips
    if displaySetup:
        totalText = DISP_TEXT + str(octaveNum)
        drawDisplaySetup(screen, totalText)
    pygame.display.update()

pygame.quit()
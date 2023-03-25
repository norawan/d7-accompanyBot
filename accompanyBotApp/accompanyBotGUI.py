import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # remove self-advertisement

from constants import *
from procedures import *
from fileOpener import openFile
from threading import Thread
from PIL import Image
import time
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
omrStarted = False
musicScoreFile = ""
musicPages=[]
device = "None"
numMeasures = 23
curMeasure = 0
userHasOrb=False
orbPos=(ORBX, ORBY)
tempo=100
oldKeyPressTime=0
newKeyPressTime=0


while running:
    keysPressed = pygame.key.get_pressed() # might be expensive
    mouseX, mouseY = pygame.mouse.get_pos()
    
    if omrStarted and not omrThread.is_alive(): # OMR finished processing
        omrOutput = omrThread.join()
        if omrOutput is None:
            print("Audiveris failed to process image input")
        else:
            print("breaking: " + musicScoreFile)
            musicPages = breakPages(musicScoreFile) # wrapper for png vs pdf files
            pass # TODO pipe xml into player
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
                omrThread=ThreadReturn(target=processMusic, args=(musicScoreFile, AUDIVERIS_OUTPUT_LOCATION))
                omrThread.start()
                omrStarted = True
 
    curMeasure = updateCurrentMeasure(screen, userHasOrb, curMeasure, numMeasures, mouseX) # update current measure with mouse
    orbPos = updateMeasureOrb(curMeasure, numMeasures, orbPos) # match orb position to current measure
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
            oldKeyPressTime = newKeyPressTime
    elif keysPressed[K_RIGHT]:
        newKeyPressTime = time.time_ns()
        if newKeyPressTime > (oldKeyPressTime + INPUT_BUFFER):
            curMeasure = goNextMeasure(curMeasure, numMeasures)
            oldKeyPressTime = newKeyPressTime

    for event in pygame.event.get(): # event loop
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                pass
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
            if mouseInButton(objects[0], mouseX, mouseY): # pdf/png button click
                if not explorerThread.is_alive():
                    explorerThread = ThreadReturn(target=openFile)
                    explorerStarted = True
                    explorerThread.start()
            elif mouseInButton(objects[1], mouseX, mouseY):
                print("Connect to Device") # TODO implement device connection logic
            elif mouseInTriangle(objects[9], mouseX, mouseY): # increase tempo
                tempo = increaseTempo(tempo) # TODO add threshold parameter
            elif mouseInTriangle(objects[10], mouseX, mouseY): # decrease tempo
                tempo = decreaseTempo(tempo)
            elif showing[11] and mouseInTriangle(objects[11], mouseX, mouseY): # play
                showing[11] = not showing[11]
                showing[18] = not showing[18]
                showing[19] = not showing[19]
            elif (not showing[11]) and mouseInPauseButton(objects[18], objects[19], mouseX, mouseY):
                showing[11] = not showing[11]
                showing[18] = not showing[18]
                showing[19] = not showing[19]
            elif mouseInTriangle(objects[12], mouseX, mouseY): # next measure
                curMeasure = goNextMeasure(curMeasure, numMeasures)
            elif mouseInTriangle(objects[13], mouseX, mouseY): # prev measure
                curMeasure = goPrevMeasure(curMeasure)
            elif mouseInCircle(objects[16], radii[16], mouseX, mouseY): # clicking in slider
                userHasOrb = True
            pass
        elif event.type == MOUSEBUTTONUP:
            userHasOrb = False


    screen.fill(BACKGROUND)
    drawObjects(screen, objects, colors, radii, showing)
    drawMusic(screen, musicPages) # TODO incorporate some indicator to determine page flips
    pygame.display.update()

pygame.quit()
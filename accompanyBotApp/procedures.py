import pygame
from constants import *
from unzip import *
import subprocess
from os import path
import os
from pdf2image import convert_from_path
from PIL import Image
from time import sleep

def mouseInButton(button : pygame.Rect, mouseX, mouseY):
    return mouseX >= button.left and mouseX <= button.right \
        and mouseY >= button.top and mouseY <= button.bottom

def mouseInPauseButton(pauseLeft : pygame.Rect, pauseRight : pygame.Rect, mouseX, mouseY):
    fullButton = pauseLeft.union(pauseRight)
    return mouseInButton(fullButton, mouseX, mouseY)

# triHelper derived from https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
def triHelper(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

# help for mouseInTriangle from https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
def mouseInTriangle(coordinates : tuple, mouseX, mouseY):
    point = (mouseX, mouseY)
    (p1, p2, p3) = coordinates

    d1 = triHelper(point, p1, p2)
    d2 = triHelper(point, p2, p3)
    d3 = triHelper(point, p3, p1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)

def breakPages(musicScoreFile):
    # assuming musicScoreFile is valid
    if musicScoreFile[-4:] == ".png":
        image = Image.open(musicScoreFile)
        return [image]
    else:
        assert(musicScoreFile[-4:] == ".pdf")
        images = convert_from_path(musicScoreFile, poppler_path=POPPLER_PATH)
        return images


def pullVerticalTriangleCoordinates(coordinate : tuple, pullDistance):
    x1, y1 = coordinate
    y2 = y1 + pullDistance
    y3 = y2
    halfPullDistance = pullDistance // 2
    x2 = x1 - halfPullDistance
    x3 = x1 + halfPullDistance
    return ((x1, y1), (x2, y2), (x3, y3))

def addMeasureForSend(toSend, curMeasure):
    toSend[MEASURE_COMMAND] = "C" + str(curMeasure) + "\n"

def swapCoords(coordinates : tuple):
    L = []
    for (x, y) in coordinates:
        L.append((y, x))
    return tuple(L)

# handle with care
def deleteProcessedOutput(subdirectory : str):
    windowsLocation = AUDIVERIS_OUTPUT_LOCATION #"C:/Users/khand/OneDrive/Documents/GitHub/d7-accompanyBot/Outputs"
    if len(subdirectory) < 1:
        print("Error: Erroneous deletion attempted with subdirectory: " + subdirectory)
    else:
        deleteScript = "C:/Users/khand/OneDrive/Documents/GitHub/d7-accompanyBot/Scripts/deleteFolder.ps1"
        rmFolderFlag = "-rmFolder"
        fullLocation = f'{windowsLocation}/{subdirectory}'
        subprocess.Popen(["powershell.exe", deleteScript, rmFolderFlag, fullLocation])
        return
        
        print("this is it: " + fullLocation)
        os.system(f'{DELETE_CMD} {fullLocation} {FORCE_FLAG} {RECURSE_FLAG}')

def processMusic(fileString, outputString, extraThreadAlert):
    pathToAudiShell = "C:/Users/khand/OneDrive/Documents/GitHub/d7-accompanyBot/Scripts/runAudiveris.ps1"
    musicxmlCache = "C:/Users/khand/OneDrive/Documents/GitHub/d7-accompanyBot/CachedMusicXML"
    argStringName = "-argString"
    outputStringName = "-outputString"

    abstractFile = clearpath(fileString).replace(".pdf", "").replace(".png", "").replace(".jpg", "") # better ways to do this
    returnFile = f'{musicxmlCache}/{abstractFile}.xml'
    if path.exists(returnFile):
        extraThreadAlert[CURRENT_XML] = f'{abstractFile}.xml'
        extraThreadAlert[CACHE_REQUEST] = True

        while extraThreadAlert[CACHE_REQUEST] == True: # spin cycle for user input
            sleep(KILL_TIMER)
            if KILL_COMMAND in extraThreadAlert and extraThreadAlert[KILL_COMMAND] == True:
                return
        
        if extraThreadAlert[CACHE_REQUEST] == EXISTING_FILE:
            return returnFile

    print("Reading sheet music...")
    readProc = subprocess.Popen(["powershell.exe", pathToAudiShell, argStringName, fileString, outputStringName, outputString], stderr=subprocess.PIPE)
    #readProc = subprocess.Popen(['Start-Process "C:\\Program Files\\Audiveris\\bin\\Audiveris"', f"\"-export -batch {fileString} -output {outputString}\""])
    while readProc.poll() is None:
        sleep(KILL_TIMER)
        if KILL_COMMAND in extraThreadAlert and extraThreadAlert[KILL_COMMAND] == True:
            readProc.kill()
            return

    newPath = outputString + f"/{abstractFile}/{abstractFile}.mxl"
    if path.exists(newPath):
        print("Unzipping binaries...")
        unzip(newPath, musicxmlCache)
        deleteProcessedOutput(abstractFile) # remove zipped version
        return returnFile
    else:
        return None # Audiveris failed to process
    
def mouseInCircle(circlePos, radius, mouseX, mouseY):
    (circleX, circleY) = circlePos
    distSq = ((circleX - mouseX) ** 2) + ((circleY - mouseY) ** 2)
    return (distSq <= (radius ** 2))

def updateCurrentMeasure(screen : pygame.Surface, userHasOrb, oldMeasure, numMeasures, mouseX):
    if not userHasOrb:
        return oldMeasure
    elif mouseX < (ORBX * screen.get_width() // FIGMA_SCREEN_WIDTH): # past left bound of slider
        return 0
    elif mouseX > ((ORBX + MEASURE_SLIDER_WIDTH) * screen.get_width() // FIGMA_SCREEN_WIDTH): # past right bound of slider
        return numMeasures
    else: # jumping to specific location on slider
        startDist = ORBX * screen.get_width() // FIGMA_SCREEN_WIDTH
        adjustedWidth = MEASURE_SLIDER_WIDTH * screen.get_width() // FIGMA_SCREEN_WIDTH
        jumpFactor = (mouseX - startDist) / adjustedWidth
        return round(jumpFactor * numMeasures)

def orbOnScreen(screen : pygame.Surface, orbPos):
    posX = orbPos[0] * screen.get_width() // FIGMA_SCREEN_WIDTH
    posY = orbPos[1] * screen.get_height() // FIGMA_SCREEN_HEIGHT
    return (posX, posY)

# assumes orb will be moved to curMeasure
def updateMeasureOrb(curMeasure, numMeasures, oldOrbPos):
    (_, oldOrbY) = oldOrbPos

    if numMeasures == 0: # no song
        return (ORBX, oldOrbY)
    else:
        movement = MEASURE_SLIDER_WIDTH * curMeasure // numMeasures
        newX = ORBX + movement
        return (newX, oldOrbY)
    
def goNextMeasure(curMeasure, numMeasures):
    if curMeasure >= numMeasures:
        return numMeasures
    else:
        return curMeasure + 1
    
def goPrevMeasure(curMeasure):
    if curMeasure <= 0:
        return 0
    else:
        return curMeasure - 1
    
def increaseTempo(tempo, threshold=200):
    if tempo >= threshold:
        return threshold
    else:
        return tempo + 1    

'''def createWaiting():
    waitingDict = dict()
    waitingDict["start"] = False
    waitingDict["pause"] = False
    waitingDict["measure"] = False
    waitingDict["tempo"] = False
    waitingDict["file"] = False
    waitingDict["kill"] = False
    return waitingDict'''
    
def decreaseTempo(tempo):
    if tempo <= 1:
        return 1
    else:
        return tempo - 1
    
def createTempoText(appScreen, tempo):
    leftTempoBox = LEFT_TEMPO_BOX * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    topTempoBox = TEMPO_BOX_TOP * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    tempoBoxWidth = TEMPO_BOX_WIDTH * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    tempoBoxHeight = TEMPO_BOX_HEIGHT * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    tempoBoxRect = pygame.Rect(leftTempoBox, topTempoBox, tempoBoxWidth, tempoBoxHeight)
    largeFontSize = LARGE_FONT_FACTOR * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    metricFont = pygame.font.SysFont("arial", largeFontSize, bold=False)
    tempoNumText = metricFont.render(str(tempo), True, BLACK, WHITE)
    tempoNumRect = tempoNumText.get_rect()
    tempoNumRect.center = tempoBoxRect.center
    
    return (tempoNumText, tempoNumRect)

def createMeasureNumText(appScreen, curMeasure):
    leftTempoBox = LEFT_TEMPO_BOX * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    topTempoBox = TEMPO_BOX_TOP * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    tempoBoxWidth = TEMPO_BOX_WIDTH * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    tempoBoxHeight = TEMPO_BOX_HEIGHT * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    tempoBoxRect = pygame.Rect(leftTempoBox, topTempoBox, tempoBoxWidth, tempoBoxHeight)

    largeFontSize = LARGE_FONT_FACTOR * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    metricFont = pygame.font.SysFont("arial", largeFontSize, bold=False)
    tempoText = metricFont.render("Tempo:", True, GOLD, BACKGROUND)
    tempoRect = tempoText.get_rect()
    tempoRect.centery = tempoBoxRect.centery
    tempoRect.left = METRIC_TAB * appScreen.get_width() // FIGMA_SCREEN_WIDTH

    measureFont = pygame.font.SysFont("arial", largeFontSize, bold=False)
    measureFont.set_underline(True)
    measureText = measureFont.render("Current Measure:", True, PINK, BACKGROUND)
    measureRect = measureText.get_rect()
    measureRect.left = tempoRect.left
    measureRect.top = tempoRect.bottom + (METRICS_HEIGHT_OFFSET * appScreen.get_height() // FIGMA_SCREEN_HEIGHT)

    measureNumFont = pygame.font.SysFont("arial", largeFontSize, bold=False)
    measureNumText = measureNumFont.render(str(curMeasure), True, PINK, BACKGROUND)
    measureNumRect = measureNumText.get_rect()
    measureNumRect.centery = measureRect.centery
    measureNumRect.left = measureRect.right + (METRIC_WIDTH_OFFSET * appScreen.get_width() // FIGMA_SCREEN_WIDTH)
    return (measureNumText, measureNumRect)

def createObjects(appScreen : pygame.Surface, device="None", orbPos=(ORBX, ORBY), tempo=100, curMeasure=0):
    objects = []

    leftIndent = appScreen.get_width() * LEFT_TAB // FIGMA_SCREEN_WIDTH
    importButtonTop = appScreen.get_height() * IMPORT_TOP // FIGMA_SCREEN_HEIGHT
    blueButtonWidth = appScreen.get_width() * BLUE_WIDTH // FIGMA_SCREEN_WIDTH
    blueButtonHeight = appScreen.get_height() * BLUE_HEIGHT // FIGMA_SCREEN_HEIGHT
    bubbleHeight = appScreen.get_height() * BUBBLE_HEIGHT // FIGMA_SCREEN_HEIGHT

    selectDeviceButtonTop = appScreen.get_height() * SELECT_DEVICE_TOP // FIGMA_SCREEN_HEIGHT
    selectionBubbleTop = appScreen.get_height() * SELECTED_BUBBLE_TOP // FIGMA_SCREEN_HEIGHT

    buttonRect1 = pygame.Rect(leftIndent, importButtonTop, blueButtonWidth, blueButtonHeight)
    buttonRect2 = pygame.Rect(leftIndent, selectDeviceButtonTop, blueButtonWidth, blueButtonHeight)
    deviceSelectedDisplay = pygame.Rect(leftIndent, selectionBubbleTop, blueButtonWidth, bubbleHeight)

    fontSize = REGULAR_FONT_FACTOR * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    buttonFont = pygame.font.SysFont("arial", fontSize, bold=True)
    imageButtonText = buttonFont.render("Import Music PDF/PNG", True, WHITE, SKY_BLUE)
    imageTextRect = imageButtonText.get_rect()
    imageTextRect.center = buttonRect1.center

    leftTempoBox = LEFT_TEMPO_BOX * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    topTempoBox = TEMPO_BOX_TOP * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    tempoBoxWidth = TEMPO_BOX_WIDTH * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    tempoBoxHeight = TEMPO_BOX_HEIGHT * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    tempoBoxRect = pygame.Rect(leftTempoBox, topTempoBox, tempoBoxWidth, tempoBoxHeight)

    largeFontSize = LARGE_FONT_FACTOR * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    metricFont = pygame.font.SysFont("arial", largeFontSize, bold=False)
    tempoText = metricFont.render("Tempo:", True, GOLD, BACKGROUND)
    tempoRect = tempoText.get_rect()
    tempoRect.centery = tempoBoxRect.centery
    tempoRect.left = METRIC_TAB * appScreen.get_width() // FIGMA_SCREEN_WIDTH

    tempoNumText = metricFont.render(str(tempo), True, BLACK, WHITE)
    tempoNumRect = tempoNumText.get_rect()
    tempoNumRect.center = tempoBoxRect.center

    measureFont = pygame.font.SysFont("arial", largeFontSize, bold=False)
    measureFont.set_underline(True)
    measureText = measureFont.render("Current Measure:", True, PINK, BACKGROUND)
    measureRect = measureText.get_rect()
    measureRect.left = tempoRect.left
    measureRect.top = tempoRect.bottom + (METRICS_HEIGHT_OFFSET * appScreen.get_height() // FIGMA_SCREEN_HEIGHT)

    measureNumFont = pygame.font.SysFont("arial", largeFontSize, bold=False)
    measureNumText = measureNumFont.render(str(curMeasure), True, PINK, BACKGROUND)
    measureNumRect = measureNumText.get_rect()
    measureNumRect.centery = measureRect.centery
    measureNumRect.left = measureRect.right + (METRIC_WIDTH_OFFSET * appScreen.get_width() // FIGMA_SCREEN_WIDTH)

    selectPlayerText = buttonFont.render("Connect to Player Device", True, WHITE, SKY_BLUE)
    selectTextRect = selectPlayerText.get_rect()
    selectTextRect.center = buttonRect2.center

    deviceSelectionFont = pygame.font.SysFont("arial", fontSize, bold=True)
    deviceSelectionFont.set_underline(True)
    deviceSelectedText = deviceSelectionFont.render("Device Selected", True, GREEN, WHITE_GRAY)
    deviceSelectRect = deviceSelectedText.get_rect()
    deviceSelectRect.centerx = deviceSelectedDisplay.centerx
    deviceSelectRect.centery = deviceSelectedDisplay.top + (DEVICE_SELECTED_OFFSET * appScreen.get_height() // FIGMA_SCREEN_HEIGHT)

    deviceFont = pygame.font.SysFont("arial", fontSize, bold=False)
    deviceText = deviceFont.render(device, True, BLACK, WHITE_GRAY)
    deviceRect = deviceText.get_rect()
    deviceRect.center = deviceSelectedDisplay.center

    incrementerX = INCREMENTER_LEFT * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    incrementerY =  INCREMENTER_TOP * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    incrementerHeight = AUGMENTER_HEIGHT * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    incrementerCoordinates = pullVerticalTriangleCoordinates((incrementerX, incrementerY), incrementerHeight)
    decrementerX = incrementerX
    decrementerY = DECREMENTER_BOTTOM * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    decrementerHeight = -incrementerHeight
    decrementerCoordinates = pullVerticalTriangleCoordinates((decrementerX, decrementerY), decrementerHeight)

    playX = PLAY_BUTTON_LEFT * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    playY = PLAY_BUTTON_TOP * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    playHeight = -PLAY_HEIGHT * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    playCoordinatesReversed = pullVerticalTriangleCoordinates((playY, playX), playHeight)
    playCoordinates = swapCoords(playCoordinatesReversed)

    pauseWidth = -playHeight // 3
    pauseHeight = -playHeight
    pauseRightX = playX - pauseWidth
    pauseRightY = playY - pauseHeight // 2
    pauseLeftY = pauseRightY
    pauseLeftX = pauseRightX - 2 * pauseWidth
    pauseLeftBarRect = pygame.Rect(pauseLeftX, pauseLeftY, pauseWidth, pauseHeight)
    pauseRightBarRect = pygame.Rect(pauseRightX, pauseRightY, pauseWidth, pauseHeight)

    nextMeasureX = (PLAY_BUTTON_LEFT + NEXT_MEASURE_OFFSET) * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    nextMeasureY = (PLAY_BUTTON_TOP + (PLAY_HEIGHT / NEXT_BUTTON_REFACTOR)) * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    nextMeasureHeight = int(playHeight * (1 - (2 * (1 / NEXT_BUTTON_REFACTOR))))
    nextMeasureCoordsReversed = pullVerticalTriangleCoordinates((nextMeasureY, nextMeasureX), nextMeasureHeight)
    nextMeasureCoordinates = swapCoords(nextMeasureCoordsReversed)

    prevMeasureX = (PLAY_BUTTON_LEFT - NEXT_MEASURE_OFFSET - PLAY_HEIGHT) * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    prevMeasureY = nextMeasureY
    prevMeasureHeight = -nextMeasureHeight
    prevMeasureCoordsReversed = pullVerticalTriangleCoordinates((prevMeasureY, prevMeasureX), prevMeasureHeight)
    prevMeasureCoordinates = swapCoords(prevMeasureCoordsReversed)

    bpmText = metricFont.render("BPM", True, GOLD, BACKGROUND)
    bpmRect = bpmText.get_rect()
    bpmRect.centery = tempoRect.centery
    bpmRect.left = (INCREMENTER_LEFT + AUGMENTER_HEIGHT) * appScreen.get_width() // FIGMA_SCREEN_WIDTH

    measureSliderX = MEASURE_SLIDER_X * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    measureSliderY = MEASURE_SLIDER_Y * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    msWidth = MEASURE_SLIDER_WIDTH * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    msThick = MEASURE_SLIDER_THICKNESS * appScreen.get_height() // FIGMA_SCREEN_HEIGHT
    measureSliderLine = (measureSliderX, measureSliderY, msWidth, msThick)

    measureOrbX = orbPos[0] * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    measureOrbY = orbPos[1] * appScreen.get_height() // FIGMA_SCREEN_HEIGHT

    leftGreen = appScreen.get_width() * GREEN_BUTTON_X // FIGMA_SCREEN_WIDTH
    greenButtonTop = appScreen.get_height() * GREEN_BUTTON_Y // FIGMA_SCREEN_HEIGHT
    greenButtonWidth = appScreen.get_width() * GREEN_BUTTON_WIDTH // FIGMA_SCREEN_WIDTH
    greenButtonHeight = appScreen.get_height() * GREEN_BUTTON_HEIGHT // FIGMA_SCREEN_HEIGHT
    greenRect = pygame.Rect(leftGreen, greenButtonTop, greenButtonWidth, greenButtonHeight)

    leftOrange = appScreen.get_width() * ORANGE_BUTTON_X // FIGMA_SCREEN_WIDTH
    orangeButtonTop = appScreen.get_height() * ORANGE_BUTTON_Y // FIGMA_SCREEN_HEIGHT
    orangeButtonWidth = appScreen.get_width() * ORANGE_BUTTON_WIDTH // FIGMA_SCREEN_WIDTH
    orangeButtonHeight = appScreen.get_height() * ORANGE_BUTTON_HEIGHT // FIGMA_SCREEN_HEIGHT
    orangeRect = pygame.Rect(leftOrange, orangeButtonTop, orangeButtonWidth, orangeButtonHeight)

    greenButtonText = buttonFont.render("Use Existing File", True, WHITE, GREEN_BUTTON_COLOR)
    greenTextRect = greenButtonText.get_rect()
    greenTextRect.center = greenRect.center

    orangeButtonText = buttonFont.render("Reprocess Music", True, WHITE, ORANGE_BUTTON_COLOR)
    orangeTextRect = orangeButtonText.get_rect()
    orangeTextRect.center = orangeRect.center

    objects.append(buttonRect1) # 0
    objects.append(buttonRect2) # 1
    objects.append(deviceSelectedDisplay) # 2
    objects.append((imageButtonText, imageTextRect)) # 3
    objects.append((selectPlayerText, selectTextRect)) # 4
    objects.append((tempoText, tempoRect)) # 5
    objects.append((deviceSelectedText, deviceSelectRect)) # 6
    objects.append((deviceText, deviceRect)) # 7
    objects.append(tempoBoxRect) # 8
    objects.append(incrementerCoordinates) # 9
    objects.append(decrementerCoordinates) # 10
    objects.append(playCoordinates) # 11
    objects.append(nextMeasureCoordinates) # 12
    objects.append(prevMeasureCoordinates) # 13
    objects.append((bpmText, bpmRect)) # 14
    objects.append(measureSliderLine) # 15
    objects.append((measureOrbX, measureOrbY)) # 16
    objects.append((tempoNumText, tempoNumRect)) # 17
    objects.append(pauseLeftBarRect) # 18
    objects.append(pauseRightBarRect) # 19
    objects.append((measureText, measureRect)) # 20
    objects.append((measureNumText, measureNumRect)) # 21
    objects.append(greenRect) # 22
    objects.append(orangeRect) # 23
    objects.append((greenButtonText, greenTextRect)) # 24
    objects.append((orangeButtonText, orangeTextRect)) # 25
    return objects

def createColors():
    colors = []

    colors.append(SKY_BLUE)
    colors.append(SKY_BLUE)
    colors.append(WHITE_GRAY)
    colors.append(None)
    colors.append(None)
    colors.append(None)
    colors.append(None)
    colors.append(None)
    colors.append(WHITE)
    colors.append(CYAN)
    colors.append(CYAN)
    colors.append(GRAY)
    colors.append(RED)
    colors.append(RED)
    colors.append(None)
    colors.append(DARK_GRAY)
    colors.append(DARK_GRAY)
    colors.append(None)
    colors.append(GRAY) 
    colors.append(GRAY)
    colors.append(None)
    colors.append(None)
    colors.append(GREEN_BUTTON_COLOR)
    colors.append(ORANGE_BUTTON_COLOR)
    colors.append(None)
    colors.append(None)
    return colors

def createRadii(appScreen : pygame.Surface):
    radii = []

    blueButtonRadius = appScreen.get_height() * BLUE_RADIUS // FIGMA_SCREEN_HEIGHT
    bubbleRadius = appScreen.get_height() * BUBBLE_RADIUS // FIGMA_SCREEN_HEIGHT
    orbRadius = 1
    if appScreen.get_height() < appScreen.get_width():
        orbRadius = appScreen.get_height() * ORB_RADIUS // FIGMA_SCREEN_HEIGHT
    else:
        orbRadius = appScreen.get_width() * ORB_RADIUS // FIGMA_SCREEN_WIDTH
    
    radii.append(blueButtonRadius)
    radii.append(blueButtonRadius)
    radii.append(bubbleRadius)
    radii.append(None)
    radii.append(None)
    radii.append(None)
    radii.append(None)
    radii.append(None)
    radii.append(blueButtonRadius)
    radii.append(None)
    radii.append(None)
    radii.append(None)
    radii.append(None)
    radii.append(None)
    radii.append(None)
    radii.append(None)
    radii.append(orbRadius)
    radii.append(None)
    radii.append(blueButtonRadius)
    radii.append(blueButtonRadius)
    radii.append(None)
    radii.append(None)
    radii.append(blueButtonRadius)
    radii.append(blueButtonRadius)
    radii.append(None)
    radii.append(None)
    return radii

def drawObjects(screen : pygame.Surface, objects : list, colors : list[pygame.Color], radii : list[int], showing : list[bool]):
    counter = -1
    for item in objects:
        counter += 1
        if not showing[counter]: continue

        if type(item) == pygame.Rect:
            pygame.draw.rect(screen, colors[counter], item, border_radius=radii[counter])
        elif type(item) == tuple and len(item) == 2 and \
            type(item[0]) == pygame.Surface and type(item[1]) == pygame.Rect: # textRect
            screen.blit(item[0], item[1])
        elif type(item) == tuple and len(item) == 3 and \
            type(item[0]) == type(item[1]) == type(item[2]) == tuple: # triangle
            pygame.draw.polygon(screen, colors[counter], item)
        elif type(item) == tuple and len(item) == 4 and \
            type(item[0]) == type(item[1]) == type(item[2]) == type(item[3]) == int: # line
            end_pos = item[0] + item[2]
            pygame.draw.line(screen, colors[counter], (item[0], item[1]), (end_pos, item[1]), item[3])
        elif type(item) == tuple and len(item) == 2 and \
            type(item[0]) == type(item[1]) == int: # circle
            pygame.draw.circle(screen, colors[counter], item, radii[counter])
        else:
            print(f"Drawing Error. Type found: {type(item)}")
    return

def drawMusic(screen : pygame.Surface, musicPages : list[Image.Image], drawFlag):
    if musicPages == []:
        return
    elif drawFlag: # for now just draw first page
        showingPage = musicPages[0]
        sRatio = showingPage.height / showingPage.width
        maxRatio = MAX_MUSIC_HEIGHT / MAX_MUSIC_WIDTH
        (fixedWidth, fixedHeight) = (0, 0)
        if sRatio > maxRatio: # height in excess
            fixedHeight = MAX_MUSIC_HEIGHT * screen.get_height() // FIGMA_SCREEN_HEIGHT
            fixedWidth = int(fixedHeight / sRatio)
        else: # width in excess
            fixedWidth = MAX_MUSIC_WIDTH * screen.get_width() // FIGMA_SCREEN_WIDTH
            fixedHeight = int(fixedWidth * sRatio)

        newImage = showingPage.resize((fixedWidth, fixedHeight))
        mode = newImage.mode
        data = newImage.tobytes()

        musicCenterX = MUSIC_CENTER_X * screen.get_width() // FIGMA_SCREEN_WIDTH
        musicCenterY = MUSIC_CENTER_Y * screen.get_height() // FIGMA_SCREEN_HEIGHT

        musicShowing = pygame.image.fromstring(data, (fixedWidth, fixedHeight), mode)
        musicRect = musicShowing.get_rect()
        musicRect.center = (musicCenterX, musicCenterY)
        screen.blit(musicShowing, musicRect)

def drawDisplaySetup(screen : pygame.Surface, text : str):
    fixFactorW = FIX_FACTOR * screen.get_width() // FIGMA_SCREEN_WIDTH
    fixFactorH = FIX_FACTOR * screen.get_height() // FIGMA_SCREEN_HEIGHT
    left = screen.get_width() // 4 + fixFactorW / 2
    top = screen.get_height() // 4 + fixFactorH / 2
    width = 2 * (left - fixFactorW)
    height = 2 * (top - fixFactorH)
    radius = screen.get_height() * BLUE_RADIUS // FIGMA_SCREEN_HEIGHT
    bodyRect = pygame.Rect(left, top, width, height)

    dialogColor = GRAY
    pygame.draw.rect(screen, dialogColor, bodyRect, border_radius=radius)

    textWidth = width // 4
    textHeight = height // 4
    leftTextBox = (left + (width // 2)) - (textWidth // 2)
    topTextBox = ((top + height) // 2) + (textHeight // 2)
    
    
    textRect = pygame.Rect(leftTextBox, topTextBox, textWidth, textHeight)
    largeFontSize = LARGE_FONT_FACTOR * screen.get_width() // FIGMA_SCREEN_WIDTH
    metricFont = pygame.font.SysFont("arial", largeFontSize, bold=False)
    textRender = metricFont.render(text, True, BLACK, dialogColor)
    realTextRect = textRender.get_rect()
    realTextRect.center = textRect.center
    screen.blit(textRender, realTextRect)

    


    '''fontSize = REGULAR_FONT_FACTOR * screen.get_width() // FIGMA_SCREEN_WIDTH
    buttonFont = pygame.font.SysFont("arial", fontSize, bold=False)
    imageAlertText = buttonFont.render(text, True, WHITE, SKY_BLUE)
    imageRectangle = screen.get_rect()
    screen.blit(imageAlertText, imageRectangle)'''

# wrap text function adapted from https://stackoverflow.com/questions/49432109/how-to-wrap-text-in-pygame-using-pygame-font-font
def wrapText(text, font, colour, x, y, screen, allowed_width, y_offset):
    # first, split the text into words
    words = text.split()

    # now, construct lines out of these words
    lines = []
    while len(words) > 0:
        # get as many words as will fit within allowed_width
        line_words = []
        while len(words) > 0:
            line_words.append(words.pop(0))
            fw, fh = font.size(' '.join(line_words + words[:1]))
            if fw > allowed_width:
                break

        # add a line consisting of those words
        line = ' '.join(line_words)
        lines.append(line)

    # now we've split our text into lines that fit into the width, actually
    # render them

    # we'll render each line below the last, so we need to keep track of
    # the culmative height of the lines we've rendered so far
    ty = y
    for line in lines:
        fw, fh = font.size(line)

        # (tx, ty) is the top-left of the font surface
        tx = x - fw / 2

        font_surface = font.render(line, True, colour)
        screen.blit(font_surface, (tx, ty))
        ty = ty + y_offset

def drawCacheMessage(extraThreadAlert, screen : pygame.Surface, showing):
    if CACHE_REQUEST in extraThreadAlert and extraThreadAlert[CACHE_REQUEST] == True:
        cacheFontSize = CACHE_TEXT_FONT * screen.get_width() // FIGMA_SCREEN_WIDTH
        cacheFont = pygame.font.SysFont("arial", cacheFontSize, bold=False)
        fcx = BLOCK_TEXT_X + (BLOCK_TEXT_WIDTH // 2)
        fcy = BLOCK_TEXT_Y
        cx = fcx * screen.get_width() // FIGMA_SCREEN_WIDTH
        cy = fcy * screen.get_height() // FIGMA_SCREEN_HEIGHT
        maxWidth = BLOCK_TEXT_WIDTH * screen.get_width() // FIGMA_SCREEN_WIDTH

        blockRectLeft = BLOCK_MESSAGE_X * screen.get_width() // FIGMA_SCREEN_WIDTH
        blockRectTop = BLOCK_MESSAGE_Y * screen.get_height() // FIGMA_SCREEN_HEIGHT
        blockRectWidth = BLOCK_MESSAGE_WIDTH * screen.get_width() // FIGMA_SCREEN_WIDTH
        blockRectHeight = BLOCK_MESSAGE_HEIGHT * screen.get_height() // FIGMA_SCREEN_HEIGHT
        cacheBlockRect = pygame.Rect(blockRectLeft, blockRectTop, blockRectWidth, blockRectHeight)
        blockBorder = BLOCK_RADIUS * screen.get_width() // FIGMA_SCREEN_WIDTH
        pygame.draw.rect(screen, BLOCK_MESSAGE_COLOR, cacheBlockRect, border_radius=blockBorder)
        wrapText(extraThreadAlert[CURRENT_XML] + PARTIAL_EXIST_STR, cacheFont, CACHE_TEXT_COLOR, cx, cy, screen, maxWidth, cacheFontSize)

        showing[22] = True
        showing[23] = True
        showing[24] = True
        showing[25] = True
    else:
        showing[22] = False
        showing[23] = False
        showing[24] = False
        showing[25] = False

def createShowParams(L):
    showing = [True] * len(L)
    showing[18] = False
    showing[19] = False
    showing[22] = False
    showing[23] = False
    showing[24] = False
    showing[25] = False
    return showing

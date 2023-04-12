import pygame
from constants import *
from unzip import *
import subprocess
from os import path
from pdf2image import convert_from_path
from PIL import Image

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

def swapCoords(coordinates : tuple):
    L = []
    for (x, y) in coordinates:
        L.append((y, x))
    return tuple(L)

def processMusic(fileString, outputString):
    pathToAudiShell = "C:/Users/khand/OneDrive/Documents/GitHub/d7-accompanyBot/Scripts/runAudiveris.ps1"
    musicxmlCache = "C:/Users/khand/OneDrive/Documents/GitHub/d7-accompanyBot/CachedMusicXML"
    argStringName = "-argString"
    outputStringName = "-outputString"

    print("Reading sheet music...")
    readProc = subprocess.Popen(["powershell.exe", pathToAudiShell, argStringName, fileString, outputStringName, outputString], stderr=subprocess.PIPE)
    readProc.wait()

    print("Unzipping binaries...")
    abstractFile = clearpath(fileString).replace(".pdf", "").replace(".png", "").replace(".jpg", "") # better ways to do this
    newPath = outputString + f"/{abstractFile}/{abstractFile}.mxl"
    if path.exists(newPath):
        unzip(newPath, musicxmlCache)
        return f'{musicxmlCache}/{abstractFile}.xml'
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

    selectPlayerText = buttonFont.render("Select Player Device", True, WHITE, SKY_BLUE)
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

def drawMusic(screen : pygame.Surface, musicPages : list[Image.Image]):
    if musicPages == []:
        return
    else: # for now just draw first page
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

def createShowParams(L):
    showing = [True] * len(L)
    showing[18] = False
    showing[19] = False
    return showing
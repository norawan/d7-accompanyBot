import pygame
from constants import *

def mouseInButton(button : pygame.Rect, mouseX, mouseY):
    return mouseX >= button.left and mouseX <= button.right \
        and mouseY >= button.top and mouseY <= button.bottom

def createObjects(appScreen : pygame.Surface):
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
    buttonFont = pygame.font.SysFont("shreedevanagari714", fontSize, bold=True)
    imageButtonText = buttonFont.render("Import Music PDF/PNG", True, WHITE, SKY_BLUE)
    imageTextRect = imageButtonText.get_rect()
    imageTextRect.center = buttonRect1.center

    largeFontSize = LARGE_FONT_FACTOR * appScreen.get_width() // FIGMA_SCREEN_WIDTH
    metricFont = pygame.font.SysFont("shreedevangari714", largeFontSize, bold=False)
    tempoText = metricFont.render("Tempo:", True, GOLD, BACKGROUND)
    leftTempo = appScreen.get_width() * METRIC_TAB // FIGMA_SCREEN_WIDTH
    topTempo = appScreen.get_height() * TEMPO_TOP // FIGMA_SCREEN_HEIGHT
    widthTempo = appScreen.get_width() * TEMPO_WIDTH // FIGMA_SCREEN_WIDTH
    heightTempo = appScreen.get_height() * TEMPO_HEIGHT // FIGMA_SCREEN_HEIGHT
    tempoRect = pygame.Rect(leftTempo, topTempo, widthTempo, heightTempo)


    selectPlayerText = buttonFont.render("Select Player Device", True, WHITE, SKY_BLUE)
    selectTextRect = selectPlayerText.get_rect()
    selectTextRect.center = buttonRect2.center

    objects.append(buttonRect1) 
    objects.append(buttonRect2)
    objects.append(deviceSelectedDisplay) 
    objects.append((imageButtonText, imageTextRect))
    objects.append((selectPlayerText, selectTextRect))
    objects.append((tempoText, tempoRect))
    return objects

def createColors():
    colors = []

    colors.append(SKY_BLUE)
    colors.append(SKY_BLUE)
    colors.append(WHITE_GRAY)
    return colors

def createRadii(appScreen : pygame.Surface):
    radii = []

    blueButtonRadius = appScreen.get_height() * BLUE_RADIUS // FIGMA_SCREEN_HEIGHT
    bubbleRadius = appScreen.get_height() * BUBBLE_RADIUS // FIGMA_SCREEN_HEIGHT
    
    radii.append(blueButtonRadius)
    radii.append(blueButtonRadius)
    radii.append(bubbleRadius)

    return radii

def drawObjects(screen : pygame.Surface, objects : list, colors : list[pygame.Color], radii : list[int]):
    counter = -1
    for item in objects:
        counter += 1
        if type(item) == pygame.Rect:
            pygame.draw.rect(screen, colors[counter], item, border_radius=radii[counter])
        elif type(item) == tuple and len(item) == 2 and \
            type(item[0]) == pygame.Surface and type(item[1]) == pygame.Rect: # textRect
            screen.blit(item[0], item[1])
        else:
            print(f"Drawing Error. Type found: {type(item)}")
    return
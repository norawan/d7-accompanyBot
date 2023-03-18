import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # remove self-advertisement

from constants import *
from procedures import *
from fileOpener import user_action


pygame.init()
screen = pygame.display.set_mode((972, 700), 
                                DESIRED_EFFECTS)

pygame.display.set_caption('accompanyBot')
running = True

objects = createObjects(screen)
colors = createColors()
radii = createRadii(screen)

musicImage = pygame.image.load("../Extra Music/Charlie_Brown_Theme.png")
defaultMusic = pygame.transform.scale(musicImage, (musicImage.get_width() // 3, musicImage.get_height() // 3))
musicRect = defaultMusic.get_rect()
musicRect.center = (650, 350)
musicRect.size = (200, 200)


while running:
    keysPressed = pygame.key.get_pressed() # might be expensive
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                print("a")
                pass
            if event.key == K_DOWN:
                print("b")
                pass
        elif event.type == KEYUP:
            pass
        elif event.type == VIDEORESIZE:
            width, height = event.size
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                width = MIN_WIDTH
                height = MIN_HEIGHT
            screen = pygame.display.set_mode((width, height), DESIRED_EFFECTS)
            objects = createObjects(screen)
            radii = createRadii(screen)
        elif event.type == MOUSEBUTTONDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            if mouseInButton(objects[0], mouseX, mouseY): # pdf/png button click
                argString = user_action(os.path.expanduser('~'), "Select")
                pass
            pass


    screen.fill(BACKGROUND)
    drawObjects(screen, objects, colors, radii)
    #screen.blit(text, textRect)
    screen.blit(defaultMusic, musicRect)

    #screen.blit(ball, rect)
    #screen.blit(button, buttonRect)
    pygame.display.update()

pygame.quit()
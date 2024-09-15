#basic pygame "game loop"
import pygame
import os

#disable sound
os.environ["SDL_AUDIODRIVER"] = "dummy"
#pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pygame in Codespace")
clock = pygame.time.Clock()
running = True

while running:
    #poll for events
    #pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    #render the game

    #flip() the display to put work on screen
    pygame.display.flip()

    #limits FPS to 60
    clock.tick(60)

pygame.image.save(screen, "screenshot.png")

pygame.quit()


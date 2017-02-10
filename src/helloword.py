import pygame
from pygame.locals import *

pygame.init()

window = pygame.display.set_mode([800,600])

red = (230,80,80)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

    window.fill((40,50,180))
    pygame.draw.rect(window, red, Rect((40,40), (90,80)))

    pygame.display.update()

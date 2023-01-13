import pygame
import sys
import Tetris
import os

WIDTH,HEIGHT = 600,600
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
GRIDSIZE = (10,24)
FPS = 60
CLOCK = pygame.time.Clock()
RESOLUTION = (WIDTH//24)    #scales with window size

def main():
    pygame.init()
    GM = Tetris.GameManager(RESOLUTION,SCREEN)
    while True:
        lastEvent = None
        for event in pygame.event.get():
            lastEvent = event
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
            # Check user Input
        GM.Update(lastEvent)
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == '__main__':
    main()
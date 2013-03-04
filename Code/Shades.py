# -*- coding: UTF-8 -*-
import pygame._view ## CX FREEZE, without it we can't freeze the script
import pygame
import pymunk
import sys
from pygame.locals import *
from ColorConstants import *
from Globals import *

import larv
import Pieces
import XMLParser
import helper
import PymunkCollisions
import Engines

def main():
    while True:
        runGame()

def runGame():
    # Play background music
    pygame.mixer.music.load(SNOW_QUEEN_MUSIC)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.8)

    # Push the first engine into the world to start rolling
    WORLD.push(Engines.StartMenuEngine().engine)

    # Manage save file
    helper.deleteSaveFile()
    helper.createSaveFile()

    # Start game loop
    game_over = False
    while not game_over :
        # Fill the screen with green color
        DISPLAYSURF.fill(GREEN)

        # Show fps top left
        # helper.outputText(str(FPS_CLOCK.get_fps()), 0, 10)

        # Update the game (will update every system in the active engine)
        try: 
            WORLD.update()
        except larv.EndProgramException: # exception raised when no more engines on world stack
            helper.terminate()

if __name__ == '__main__':
    main()
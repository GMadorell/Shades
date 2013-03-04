import larv
import pygame
import Engines

from Globals import *


class StartMenuInputSystem(larv.System):
    """
    Input for the first menu, the Shades main screen.
    Only goes towards the main menu when player presses escape.
    """
    def update(self):

        # Process pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                raise larv.EndProgramException()

            elif event.type == KEYDOWN:
                # if event.key == K_ESCAPE:
                #     raise larv.EndProgramException()
                if event.key == K_SPACE:
                    WORLD.change(Engines.MainMenuEngine().engine)
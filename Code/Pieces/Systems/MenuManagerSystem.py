# -*- coding: UTF-8 -*-
import larv
import helper
import pygame

from ..Components import PositionComponent
from ..Components import StateComponent
from ..Components import LevelInfoComponent
from ..Components import MenuButtonComponent

from Globals import *

class FoundException(Exception): pass

class MenuManagerSystem(larv.System):
    """
    Does some logic of the menu, such as:
      - If there's no option selected, forces one to be active (topmost).
      - Background sound.
    """
    def __init__(self):
        self.first_time = True

    def update(self):
        list_entities = self.entity_manager.getEntitiesHavingComponents(
                                                PositionComponent.__name__,
                                                StateComponent.__name__
                                            )

        # Search if any element is active
        active = False
        for entity in list_entities:
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)
            if state_comp.state == 'active':
                active = True
                break

        # If we can't find any active element, we force the topmost to be active
        if active:
            return
        try:            
            for height in range(WIN_HEIGHT):
                for entity in list_entities:
                    position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
                    x, y = helper.xyToPygame(position_comp.x, position_comp.y)
                    if y == height:
                        raise FoundException()
        except FoundException:
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)
            state_comp.state = 'active'

        # Manage sound
        # The first time we are on this system, we stop the music and play the
        # menu music.
        if self.first_time:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.load(MENU_MUSIC)
                pygame.mixer.music.play(-1, 0.0)

        self.first_time = False
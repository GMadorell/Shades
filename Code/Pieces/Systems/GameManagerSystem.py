# -*- coding: UTF-8 -*-
import larv
import helper
import copy

from ..Components import PositionComponent
from ..Components import StateComponent
from ..Components import LevelInfoComponent
from ..Components import PhysicsComponent

from Globals import *

class GameManagerSystem(larv.System):
    """
    Manages some logic of the game, such as:
        - Check if player won
        - Remove obsolete entities (those with physics component which no longer have body
                                    due to collisions)
        - Checks the music status
    """
    def __init__(self):
        self.first_time = True

    def update(self):
        # Get hero entity
        hero = self.group_manager.get('hero')[0]

        # Get camera entity
        camera = self.group_manager.get('camera')[0]

        # Get components
        hero_pos_comp = self.entity_manager.getComponent(hero, PositionComponent.__name__)
        hero_state_comp = self.entity_manager.getComponent(hero, StateComponent.__name__)
        camera_pos_comp = self.entity_manager.getComponent(camera, PositionComponent.__name__)

        # Get level info component
        level_info = self.group_manager.get('level_info')[0]
        level_info_comp = self.entity_manager.getComponent(level_info, LevelInfoComponent.__name__)

        # Check if hero has got to the final of the level
        end = level_info_comp.player_finish
        x, y = helper.xyToPygame(end[0], end[1])
        x -= camera_pos_comp.x
        y += camera_pos_comp.y

        if hero_pos_comp.rect.collidepoint(x, y):
            hero_state_comp.state = 'win'

        # Iterate over those components that have physics component.
        # If they no longer have body or shape, delete them.
        entity_list = self.entity_manager.getEntitiesHavingComponent(PhysicsComponent.__name__)
        for entity in entity_list:
            physics_comp = self.entity_manager.getComponent(entity, PhysicsComponent.__name__)
            if physics_comp.shape.group == REMOVE_GROUP:
                self.group_manager.removeCompletely(entity)
                self.entity_manager.removeEntity(entity)


        # Check music status
        # if self.first_time:
        #     pygame.mixer.music.stop()
        #     level_name = level_info_comp.level_name
        #     pygame.mixer.music.load(MUSIC_MAP[level_name])
        #     pygame.mixer.music.play(-1, 0.0)
            
            
                    


        # Indicate that we have, at least, updated the system once
        self.first_time = False
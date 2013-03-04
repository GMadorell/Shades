import larv
import pygame
import os.path
import Engines
import helper
import pymunk

from ..Components import LevelInfoComponent
from ..Components import PositionComponent
from ..Components import PhysicsComponent
from ..Components import StateComponent
from ..Components import IntermitentComponent
from ..Components import PathComponent

from Globals import *
from ColorConstants import *


class HeroStateSystem(larv.System):
    """
    System dedicated exclusively to manage the state of the hero entity.
    """
    def update(self):
        # get the hero entity
        hero = self.group_manager.get('hero')[0]

        # get hero's components
        position_comp = self.entity_manager.getComponent(hero, PositionComponent.__name__)
        physics_comp = self.entity_manager.getComponent(hero, PhysicsComponent.__name__)
        state_comp = self.entity_manager.getComponent(hero, StateComponent.__name__)

        # get the level info component
        level_info = self.group_manager.get('level_info')[0]
        level_info_comp = self.entity_manager.getComponent(level_info, LevelInfoComponent.__name__)

        # get the state variable 
        state = state_comp.state

        #switch the state
        # if the hero is dead, we reset the level completely
        if state == 'dead':
            self.dieState(position_comp, physics_comp, state_comp, level_info_comp)
        # if the hero won
        if state == 'win':
            self.winState(position_comp, physics_comp, state_comp, level_info_comp)

    def dieState(self, position_comp, physics_comp, state_comp, level_info_comp):
        """
        Processes the state of the hero dieing.
        """  
        WORLD.addPostUpdateFunction(self.reset)

    def winState(self, position_comp, physics_comp, state_comp, level_info_comp):
        """
        Processes the state when the player wins.
        """
        current_level = level_info_comp.level_name

        # Get next level (add 1 to the number)
        next_level = 'levels\\'
        for char in current_level:
            if char.isdigit():
                next_level += str(int(char)+1)
            else:
                next_level += char

        # Add the xml tag after it
        next_level += '.xml'

        # See if the file exists
        if os.path.isfile(next_level):
            # We load the next level after a brief pause
            def nextLevel():
                pygame.time.wait(250)
                WORLD.change(Engines.LevelEngine(next_level).engine)
            WORLD.addPostUpdateFunction(nextLevel)
        else: # no more levels -> we won
            def winFunction():
                DISPLAYSURF.fill(BLACK)
                helper.outputText('YOU WIN!!',WIN_WIDTH//2, WIN_HEIGHT//2, WHITE,
                                   size = 64, centered=True)
                pygame.display.update()
                pygame.time.wait(1500)
                WORLD.pop()
            WORLD.addPostUpdateFunction(winFunction)

        # print('win', level_info_comp.level_name)

        # Save the info into the save file
        save_file = helper.getSaveFile()
        save_file[current_level]['complete'] = True
        helper.modifySaveFile(save_file)


    def reset(self):
        """
        Resets the level to it's initial state (a hard reset).
            - Sets all the positions to their initial value.
            - Sets all physical bodies to the initial position and cancels
              every momentum they may have.
            - Intermitent components get their time reset to None.
            - All laser_shot elements get deleted completely.
            - All the states get changed to their initial value.
        This is a huge optimization over charging the whole level again.
        """
        # paint black and wait a little bit
        DISPLAYSURF.fill(BLACK)
        pygame.display.update()
        pygame.time.wait(100)

        # set all positions to initial position
        list_entities = self.entity_manager.getEntitiesHavingComponents(
                                                PositionComponent.__name__
                                            )
        for entity in list_entities:
            position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
            position_comp.x = position_comp.initial_x
            position_comp.y = position_comp.initial_y

        # set all physical bodies to their corresponding new position,
        # set their velocity to zero, their angle to 0 and reset the
        # forces applied to them
        list_entities = self.entity_manager.getEntitiesHavingComponents(
                                                PositionComponent.__name__,
                                                PhysicsComponent.__name__
                                            )
        for entity in list_entities:
            position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
            physics_comp = self.entity_manager.getComponent(entity, PhysicsComponent.__name__)
            x = position_comp.x
            y = position_comp.y
            physics_comp.shape.body.position = pymunk.vec2d.Vec2d(x, y)
            physics_comp.shape.body.reset_forces()
            physics_comp.shape.body.velocity = (0,0)
            physics_comp.shape.body.angle = 0

        # set all intermittent components to time None (uninitialised)
        # see if any intermitent component does exist
        if IntermitentComponent.__name__ in self.entity_manager.components_by_class:
            list_entities = self.entity_manager.getEntitiesHavingComponents(
                                                    IntermitentComponent.__name__
                                                )
            for entity in list_entities:
                intermitent_comp = self.entity_manager.getComponent(entity,
                                              IntermitentComponent.__name__)
                intermitent_comp.time = None

        # set all state components to their initial state
        list_entities = self.entity_manager.getEntitiesHavingComponents(
                                                StateComponent.__name__
                                            )
        for entity in list_entities:
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)
            state_comp.state = state_comp.initial_state

        # delete all shots
        if self.group_manager.doesGroupExist('laser_shot'):
            list_entities = self.group_manager.get('laser_shot')
            for entity in list_entities:
                # Remove them from the physic space
                physics_comp = self.entity_manager.getComponent(entity, PhysicsComponent.__name__)
                try:
                    SPACE.remove(physics_comp.shape.body, physics_comp.shape)
                except KeyError as err:
                    print('WARNING:\nKeyError @ HeroStateSystem.py - Reset function \n{0}'.format(err))
                # Remove them from the groups
                self.group_manager.removeCompletely(entity)
                # Remove them from the entity manager
                self.entity_manager.removeEntity(entity)

        # reset path indexes to initial value
        if PathComponent.__name__ in self.entity_manager.components_by_class:
            list_entities = self.entity_manager.getEntitiesHavingComponents(
                                                    PathComponent.__name__
                                                )
            for entity in list_entities:
                path_comp = self.entity_manager.getComponent(entity,
                                              PathComponent.__name__)
                path_comp.index = path_comp.initial_index
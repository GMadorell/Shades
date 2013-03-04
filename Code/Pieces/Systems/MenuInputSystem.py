import larv
import pygame
import helper

from ..Components import MenuButtonComponent
from ..Components import StateComponent
from ..Components import RenderComponent
from ..Components import PositionComponent
from ..Components import OnPressComponent

from pygame.locals import *
from Globals import *

class FoundException(Exception): pass

class MenuInputSystem(larv.System):
    """
    Manages input while in Menu mode.
    """
    def update(self):
        list_entities = self.entity_manager.getEntitiesHavingComponents(
                                                MenuButtonComponent.__name__,
                                                StateComponent.__name__,
                                                PositionComponent.__name__,
                                                OnPressComponent.__name__
                                            )
        # Process pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                raise larv.EndProgramException()

            elif event.type == KEYDOWN:
                # if event.key == K_ESCAPE:
                #     raise larv.EndProgramException()
                if event.key == K_UP:
                    self.keyUp(list_entities)
                if event.key == K_DOWN:
                    self.keyDown(list_entities)
                if event.key == K_RIGHT:
                    self.keyRight(list_entities)
                if event.key == K_LEFT:
                    self.keyLeft(list_entities)
                if event.key == K_SPACE:
                    self.keySpace(list_entities)

    def keyUp(self, list_entities):
        """
        Sets the current active menu object to inactive and then selects
        the next element in top direction to active.
        If no element is found, it spins around and selects the botmost
        element as active.
        @list_entities: list including entities to be processed.
        """
        # Find current active entity
        for entity in list_entities:
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)
            if state_comp.state == 'active':
                active_entity = entity
                break

        # Get current location of active entity
        position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
        active_x, active_y = helper.xyToPygame(position_comp.x, position_comp.y)

        # Set current active button to inactive
        state_comp.state = 'inactive'

        # Search the next button (top direction)
        active_y -= 1
        new_entity = None
        possible_entities = []
        break_loop = False
        # First of all search for all possible entities
        for i in range(active_y, 0, -1):
            for entity in list_entities:
                position_comp = self.entity_manager.getComponent(entity,
                                                 PositionComponent.__name__)
                x, y = helper.xyToPygame(position_comp.x, position_comp.y)
                if y == i:
                    possible_entities.append(entity)
                    break_loop = True
            if break_loop: break

        # If we didn't find any entity, the before button is set to active again
        if not possible_entities:
            state_comp.state = 'active'
            return

        # If we did in fact find any new entity, select the one who is nearer
        # at a height level
        distances = []
        for entity in possible_entities:
            position_comp = self.entity_manager.getComponent(entity,
                                                 PositionComponent.__name__)
            x, y = helper.xyToPygame(position_comp.x, position_comp.y)
            distances.append( (x - active_x)**2 )
        distances = list(enumerate(distances)) # add enumeration from 0 to n
        distances.sort(key = lambda x: x[1])   # sort by distance from less to high
        n = distances[0][0] # select the enumeration of the first element after sorting
        new_entity = possible_entities[n] # the new entity will be the nearest one

        # Mark the found entity as active
        state_comp = self.entity_manager.getComponent(new_entity, StateComponent.__name__)
        state_comp.state = 'active'


        # # If we didn't find any button, start search from bottom to top
        # if not new_entity:
        #     try:
        #         for i in range(WIN_HEIGHT, 0, -1):
        #             for entity in list_entities:
        #                 position_comp = self.entity_manager.getComponent(entity,
        #                                              PositionComponent.__name__)
        #                 x, y = helper.xyToPygame(position_comp.x, position_comp.y)
        #                 if y == i:
        #                     raise FoundException()
        #     except FoundException:
        #         new_entity = entity

        # # Now that we have the new active button, just set it's status to active
        # state_comp = self.entity_manager.getComponent(new_entity, StateComponent.__name__)
        # state_comp.state = 'active'

    def keyDown(self, list_entities):
        """
        Sets the current active menu object to inactive and then selects
        the next element in down direction to active.
        If no element is found, it spins around and selects the topmost
        element as active.
        Very similar to keyUp, just different direction when searching.
        @list_entities: list including entities to be processed.
        """
        # Find current active entity
        for entity in list_entities:
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)
            if state_comp.state == 'active':
                active_entity = entity
                break

        # Get current location of active entity
        position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
        active_x, active_y = helper.xyToPygame(position_comp.x, position_comp.y)

        # Set current active button to inactive
        state_comp.state = 'inactive'

        # Search the next button (top direction)
        active_y += 1
        new_entity = None
        possible_entities = []
        break_loop = False
        # First of all search for all possible entities
        for i in range(active_y, WIN_HEIGHT, 1):
            for entity in list_entities:
                position_comp = self.entity_manager.getComponent(entity,
                                                 PositionComponent.__name__)
                x, y = helper.xyToPygame(position_comp.x, position_comp.y)
                if y == i:
                    possible_entities.append(entity)
                    break_loop = True
            if break_loop: break

        # If we didn't find any entity, the before button is set to active again
        if not possible_entities:
            state_comp.state = 'active'
            return

        # If we did in fact find any new entity, select the one who is nearer
        # at a height level
        distances = []
        for entity in possible_entities:
            position_comp = self.entity_manager.getComponent(entity,
                                                 PositionComponent.__name__)
            x, y = helper.xyToPygame(position_comp.x, position_comp.y)
            distances.append( (x - active_x)**2 )
        distances = list(enumerate(distances)) # add enumeration from 0 to n
        distances.sort(key = lambda x: x[1])   # sort by distance from less to high
        n = distances[0][0] # select the enumeration of the first element after sorting
        new_entity = possible_entities[n] # the new entity will be the nearest one

        # Mark the found entity as active
        state_comp = self.entity_manager.getComponent(new_entity, StateComponent.__name__)
        state_comp.state = 'active'

        # # If we didn't find any button, start search from bottom to top
        # if not new_entity:
        #     try:
        #         for i in range(0, WIN_HEIGHT, 1):
        #             for entity in list_entities:
        #                 position_comp = self.entity_manager.getComponent(entity,
        #                                              PositionComponent.__name__)
        #                 x, y = helper.xyToPygame(position_comp.x, position_comp.y)
        #                 if y == i:
        #                     raise FoundException()
        #     except FoundException:
        #         new_entity = entity

        # # Now that we have the new active button, just set it's status to active
        # state_comp = self.entity_manager.getComponent(new_entity, StateComponent.__name__)
        # state_comp.state = 'active'

    def keyRight(self, list_entities):
        """
        Setlects the right button in position to the actual active button if that's
        possible, else the current button remains active.
        @list_entities: list including entities to be processed.
        """
        # Find current active entity
        for entity in list_entities:
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)
            if state_comp.state == 'active':
                active_entity = entity
                break

        # Get current location of active entity
        position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
        active_x, active_y = helper.xyToPygame(position_comp.x, position_comp.y)

        # Set current active button to inactive
        state_comp.state = 'inactive'

        # Search the next button
        active_x += 1
        new_entity = None
        possible_entities = []
        break_loop = False
        # First of all search for all possible entities
        for i in range(active_x, WIN_WIDTH, 1):
            for entity in list_entities:
                position_comp = self.entity_manager.getComponent(entity,
                                                 PositionComponent.__name__)
                x, y = helper.xyToPygame(position_comp.x, position_comp.y)
                if x == i:
                    possible_entities.append(entity)
                    break_loop = True
            if break_loop: break

        # If we didn't find any entity, the before button is set to active again
        if not possible_entities:
            state_comp.state = 'active'
            return

        # If we did in fact find any new entity, select the one who is nearer
        # at a height level
        distances = []
        for entity in possible_entities:
            position_comp = self.entity_manager.getComponent(entity,
                                                 PositionComponent.__name__)
            x, y = helper.xyToPygame(position_comp.x, position_comp.y)
            distances.append( (y - active_y)**2 )
        distances = list(enumerate(distances)) # add enumeration from 0 to n
        distances.sort(key = lambda x: x[1])   # sort by distance from less to high
        n = distances[0][0] # select the enumeration of the first element after sorting
        new_entity = possible_entities[n] # the new entity will be the nearest one

        # Mark the found entity as active
        state_comp = self.entity_manager.getComponent(new_entity, StateComponent.__name__)
        state_comp.state = 'active'            
    
    def keyLeft(self, list_entities):
        """
        Setlects the left button in position to the actual active button if that's
        possible, else the current button remains active.
        @list_entities: list including entities to be processed.
        """
        # Find current active entity
        for entity in list_entities:
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)
            if state_comp.state == 'active':
                active_entity = entity
                break

        # Get current location of active entity
        position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
        active_x, active_y = helper.xyToPygame(position_comp.x, position_comp.y)

        # Set current active button to inactive
        state_comp.state = 'inactive'

        # Search the next button (top direction)
        active_x -= 1
        new_entity = None
        possible_entities = []
        break_loop = False
        # First of all search for all possible entities
        for i in range(active_x, 0, -1):
            for entity in list_entities:
                position_comp = self.entity_manager.getComponent(entity,
                                                 PositionComponent.__name__)
                x, y = helper.xyToPygame(position_comp.x, position_comp.y)
                if x == i:
                    possible_entities.append(entity)
                    break_loop = True
            if break_loop: break

        # If we didn't find any entity, the before button is set to active again
        if not possible_entities:
            state_comp.state = 'active'
            return

        # If we did in fact find any new entity, select the one who is nearer
        # at a height level
        distances = []
        for entity in possible_entities:
            position_comp = self.entity_manager.getComponent(entity,
                                                 PositionComponent.__name__)
            x, y = helper.xyToPygame(position_comp.x, position_comp.y)
            distances.append( (y - active_y)**2 )
        distances = list(enumerate(distances)) # add enumeration from 0 to n
        distances.sort(key = lambda x: x[1])   # sort by distance from less to high
        n = distances[0][0] # select the enumeration of the first element after sorting
        new_entity = possible_entities[n] # the new entity will be the nearest one

        # Mark the found entity as active
        state_comp = self.entity_manager.getComponent(new_entity, StateComponent.__name__)
        state_comp.state = 'active'

    def keySpace(self, list_entities):
        """
        Loads the function of the current active button.
        """
        # Find current active entity
        for entity in list_entities:
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)
            if state_comp.state == 'active':
                active_entity = entity
                break

        # Get onPressComponent and info
        on_press_comp = self.entity_manager.getComponent(entity, OnPressComponent.__name__)
        function = on_press_comp.function
        args = on_press_comp.args

        # for arg in args:
        #     print(arg, type(arg))
        # Run the stored function
        function(*args)


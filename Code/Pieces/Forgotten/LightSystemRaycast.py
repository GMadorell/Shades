# -*- coding: UTF-8 -*-
import larv
import helper

from ..Components import LightComponent
from ..Components import PositionComponent
from ..Components import LevelInfoComponent
from ..Components import StateComponent
from ..Components import IntermitentComponent   

from Globals import *
from ColorConstants import *

class LightSystem(larv.System):
    """
    Takes every entity that has:
        - LightComponent
    And also takes info on:
        - Camera
    And does the following actions on them:
        - Update the light
        - Create mask if it wasn't created already
        - Render them on screen
    """
    def update(self):
        #### JUST FOR DEBUG PURPOSES
        level_info = self.group_manager.get('level_info')[0]
        level_info_comp = self.entity_manager.getComponent(level_info, LevelInfoComponent.__name__)
        #########

        # Get all entities that have light and pos component
        list_entities = self.entity_manager.getEntitiesHavingComponents(
                                LightComponent.__name__,
                                PositionComponent.__name__,
                                StateComponent.__name__)

        # Get camera information
        camera = self.group_manager.get('camera')[0]
        camera_pos_component = self.entity_manager.getComponent(camera, PositionComponent.__name__)
        camera_x = camera_pos_component.x
        camera_y = camera_pos_component.y

        # Get hero's information
        hero = self.group_manager.get('hero')[0]
        hero_pos_comp = self.entity_manager.getComponent(hero, PositionComponent.__name__)
        hero_state_comp = self.entity_manager.getComponent(hero, StateComponent.__name__)

        # Fill a obstructors list with objects that must block light
        list_obstructors = self.group_manager.get('obstructor')
        obstructors = []
        for obstructor in list_obstructors:
            position_comp = self.entity_manager.getComponent(obstructor, PositionComponent.__name__)
            x, y = helper.xyToPygame(position_comp.x, position_comp.y)
            x = x - camera_x 
            y = y + camera_y 
            position_comp.rect.topleft = (x, y)
            obstructors.append(position_comp.rect)

        # Add dynamic obstructors, such as crates, to the obstructors list
        list_obstructors = self.group_manager.get('dynamic_obstructor')
        for obstructor in list_obstructors:
            position_comp = self.entity_manager.getComponent(obstructor, PositionComponent.__name__)
            obstructors.append(position_comp.rect)

        # Iterate over the light entities and update them
        for entity in list_entities:
            # Get components for current entity
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)            
            light_comp = self.entity_manager.getComponent(entity, LightComponent.__name__)
            position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)

            # If it's not active we just ignore it and continue to the next one
            if state_comp.state != 'active':
                continue

            # Reset the containers and set to the new ones
            light_comp.light.clean()
            light_comp.light.addRectList(obstructors)

            # Get info and adapt it to camera
            x, y = helper.xyToPygame(position_comp.x, position_comp.y)
            x = int(x - camera_x)
            y = int(y + camera_y)
            size = light_comp.size
            
            # Set the border (limit) of the light
            light_comp.light.setBorderWithSize(x, y, size, input = 'pygame')

            # Set position
            light_comp.light.setLightLocation(x, y, input = 'pygame')

            # Run the sweep method (create light triangles)
            light_comp.light.sweep()

            # Finally paint the light onto the screen
            light_comp.light.blit(DISPLAYSURF, light_comp.color, light_comp.alpha)

            # Check if hero is inside the light
            hero_rect = hero_pos_comp.rect
            if light_comp.light.isRectInsideLight(hero_rect):
                hero_state_comp.state = 'dead'




        #####
        #####
        ## DEBUG THINGS
        if level_info_comp.debug:
            # draw obstructors
            for obstructor in obstructors:
                pygame.draw.rect(DISPLAYSURF, BLACK, obstructor, 3)

            # draw light 
            for entity in list_entities:                
                light_comp = self.entity_manager.getComponent(entity, LightComponent.__name__)
                position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)

                # draw rect
                x, y = helper.xyToPygame(position_comp.x, position_comp.y)
                x = int(x - camera_x)
                y = int(y + camera_y)
                size = light_comp.size
                pygame.draw.rect(DISPLAYSURF, YELLOW, (x-size//2, y-size//2, size, size), 5)

                # draw light center
                pygame.draw.circle(DISPLAYSURF, RED, (x,y), 5)




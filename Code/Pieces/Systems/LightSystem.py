# -*- coding: UTF-8 -*-
import larv
import helper

from ..Components import LightComponent
from ..Components import PositionComponent
from ..Components import LevelInfoComponent
from ..Components import StateComponent

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
    def __init__(self):
        self.first_time = True # optimization

    def update(self):
        #### JUST FOR DEBUG PURPOSES
        level_info = self.group_manager.get('level_info')[0]
        level_info_comp = self.entity_manager.getComponent(level_info, LevelInfoComponent.__name__)
        ####

        # Get all the lights
        list_entities = self.entity_manager.getEntitiesHavingComponents(
                                                    LightComponent.__name__
                                                )

        # Get the camera information
        camera = self.group_manager.get('camera')[0]
        camera_pos_component = self.entity_manager.getComponent(camera, PositionComponent.__name__)
        camera_x = camera_pos_component.x
        camera_y = camera_pos_component.y

        # Get hero's information
        hero = self.group_manager.get('hero')[0]
        hero_pos_comp = self.entity_manager.getComponent(hero, PositionComponent.__name__)
        hero_state_comp = self.entity_manager.getComponent(hero, StateComponent.__name__)

        # Populate a list of the obstructors only if it's the first time we're
        # updating the system
        obstructors = []
        if self.first_time:
            if self.group_manager.doesGroupExist('obstructor'):
                list_obstructors = self.group_manager.get('obstructor')            
                for obstructor in list_obstructors:
                    position_comp = self.entity_manager.getComponent(obstructor,
                                                        PositionComponent.__name__)
                    x, y = helper.xyToPygame(position_comp.x, position_comp.y)
                    # x = x - camera_x
                    # y = y + camera_y 
                    position_comp.rect.topleft = (x, y)
                    obstructors.append(position_comp.rect)

        # Create a list for temporal (auxiliar) obstructors
        auxiliar_obstructors = []
        # Add the dynamic obstructors to that list
        if self.group_manager.doesGroupExist('dynamic_obstructor'):
            list_obstructors = self.group_manager.get('dynamic_obstructor')
            for obstructor in list_obstructors:
                position_comp = self.entity_manager.getComponent(obstructor, PositionComponent.__name__)
                auxiliar_obstructors.append(position_comp.rect)

        # Update the lights
        for entity in list_entities:
            light_comp = self.entity_manager.getComponent(entity, LightComponent.__name__)
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)

            # If mask isn't created, we initiate it
            if light_comp.light.mask is None:
                light_comp.light.createMask()

            # If the light isn't active, don't update it
            if state_comp.state != 'active':
                continue

            # Update position
            x, y = helper.xyToPygame(light_comp.light.x, light_comp.light.y)
            x = x - camera_x
            y = y + camera_y
            light_comp.light.light_rect.center = x, y
            
            # Update obstructors
            if not light_comp.light.obstructors:
                light_comp.light.setObstructors(obstructors)
            if auxiliar_obstructors:
                light_comp.light.setObstructors(auxiliar_obstructors, auxiliar=True)

            ## May need to apply some logic around the update
            ## because it may be computationally intensive.
            ## Currently, we just update if there are any dynamic obstructors and
            ## or we are on the first update
            if self.first_time:
                # Update the constructors with the camera movement
                light_comp.light.updateObstructors(camera_x, camera_y)
                # Update the camera mask
                light_comp.light.update() # Without dynamic objects we will only render the mask once!
            elif auxiliar_obstructors:
                # Update the constructors with the camera movement
                light_comp.light.updateObstructors(camera_x, camera_y)
                # Update the light (update it's mask to be rendered)
                light_comp.light.update()
                ## Only update if the any obstructor is inside the light area
                # for obstructor in auxiliar_obstructors:
                #     if light_comp.light.isRectInsideLight(obstructor, x, y,
                #                                            camera_x, camera_y):
                #         light_comp.light.update()
                #         break

            # Draw the light onto the screen
            light_comp.light.blit(DISPLAYSURF)

            # Hero is in light range -> kill him
            hero_rect = hero_pos_comp.rect
            # print(hero_rect.topleft)
            if light_comp.light.isRectInsideLight(hero_rect, x, y, camera_x, camera_y):
                hero_state_comp.state = 'dead'

            # Clean the auxiliar obstructors
            light_comp.light.cleanAuxiliar()

        # Indicate that we have, at least, updated this system once
        self.first_time = False


        #####
        #####
        ## DEBUG THINGS
        if level_info_comp.debug:
            # draw obstructors
            for entity in list_entities:
                light_comp = self.entity_manager.getComponent(entity, LightComponent.__name__)
                for obstructor in light_comp.light.obstructors + light_comp.light.auxiliar_obstructors:
                    pygame.draw.rect(DISPLAYSURF, BLACK, obstructor, 3)

            # draw light 
            for entity in list_entities:
                # draw rect
                light_comp = self.entity_manager.getComponent(entity, LightComponent.__name__)
                rect = light_comp.light.light_rect
                pygame.draw.rect(DISPLAYSURF, YELLOW, rect, 3)

                # draw middle of rect
                pygame.draw.circle(DISPLAYSURF, BLUE, rect.center, 3)



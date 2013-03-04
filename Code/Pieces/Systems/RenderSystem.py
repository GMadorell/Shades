# -*- coding: UTF-8 -*-
import larv
import helper

from ..Components import PositionComponent
from ..Components import RenderComponent
from ..Components import PhysicsComponent
from ..Components import LevelInfoComponent
from ..Components import StateComponent

from Globals import *
from ColorConstants import *

class RenderSystem(larv.System):
    """
    Takes all the components that have:
        - PositionComponent
        - RenderComponent
    and calls surface.blit on all of them (paints them on the screen).
    Also offsets them by the camera position.
    """
    def __init__(self, surface=DISPLAYSURF):
        self.surface = surface

    def update(self):
        #### JUST FOR DEBUG PURPOSES
        has_level_info = self.group_manager.doesGroupExist('level_info')
        if has_level_info:
            level_info = self.group_manager.get('level_info')[0]
            level_info_comp = self.entity_manager.getComponent(level_info, LevelInfoComponent.__name__)
        ####

        list_entities = self.entity_manager.getEntitiesHavingComponents(
                            PositionComponent.__name__,
                            RenderComponent.__name__)

        has_camera = self.group_manager.doesGroupExist('camera')
        if has_camera:
            camera_entity = self.group_manager.get('camera')[0]
            camera_position = self.entity_manager.getComponent(camera_entity, PositionComponent.__name__)
            camera_x = camera_position.x
            camera_y = camera_position.y

        for entity in list_entities:
            position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
            render_comp = self.entity_manager.getComponent(entity, RenderComponent.__name__)

            x,y = helper.xyToPygame(position_comp.x, position_comp.y)
            if has_camera:
                x -= camera_x
                y += camera_y
            position_comp.rect.centerx = x
            position_comp.rect.centery = y
            self.surface.blit(render_comp.sprite, position_comp.rect)







        #####
        #####
        ## DEBUG THINGS
        if not has_level_info:
            return
        if level_info_comp.debug:
            # paint collision
            list_entities = self.group_manager.get('collision')
            for entity in list_entities:
                # collision rectangle
                physics_comp = self.entity_manager.getComponent(entity, PhysicsComponent.__name__)
                shape = physics_comp.shape
                vertices = shape.get_points() 
                x,y = helper.toPygame(vertices[0])
                width = helper.toPygame(vertices[1])[0] - x
                height = y - helper.toPygame(vertices[3])[1]
                x = int(x - camera_x)
                y = int(y + camera_y - height)   
                rect = pygame.Rect(x, y, width, height)
                pygame.draw.rect(DISPLAYSURF, RED, rect, 3) 

                # gravity center
                center = helper.toPygame(physics_comp.body.position)
                center = (int(center[0] - camera_x), int(center[1] + camera_y))
                pygame.draw.circle(DISPLAYSURF, BLUE, center, 3)

            # paint hero center of gravity
            hero = self.group_manager.get('hero')[0]
            physics_comp = self.entity_manager.getComponent(hero, PhysicsComponent.__name__)
            center = helper.toPygame(physics_comp.body.position)
            center = (int(center[0] - camera_x), int(center[1] + camera_y))
            pygame.draw.circle(DISPLAYSURF, BLUE, center, 3)


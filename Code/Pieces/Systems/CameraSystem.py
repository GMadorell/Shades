# -*- coding: UTF-8 -*-
import larv
import helper
import math
import pygame

from ..Components import LevelInfoComponent
from ..Components import PositionComponent

from Globals import *
from ColorConstants import *

class CameraSystem(larv.System):
    """
    Takes the camera entity, the hero's position and the level info and updates
    camera position accordingly to those values.

    How to use camera from other systems:
        x,y = helper.toPygame(position_comp.position)
        position_comp.rect.centerx = x - camera_x
        position_comp.rect.centery = y + camera_y
        # Basically substract camera_x from x and add camera_y to y.
    """
    def update(self):
        camera = self.group_manager.get('camera')[0]
        hero = self.group_manager.get('hero')[0]
        level_info = self.group_manager.get('level_info')[0]

        camera_pos_component = self.entity_manager.getComponent(camera, PositionComponent.__name__)
        hero_pos_component = self.entity_manager.getComponent(hero, PositionComponent.__name__)
        level_logic_comp = self.entity_manager.getComponent(level_info, LevelInfoComponent.__name__)

        hero_x = hero_pos_component.x
        hero_y = hero_pos_component.y
        camera_x_limit_left = level_logic_comp.camera_x_limit_left
        camera_x_limit_right = level_logic_comp.camera_x_limit_right
        camera_y_limit_top = level_logic_comp.camera_y_limit_top
        camera_y_limit_bottom = level_logic_comp.camera_y_limit_bottom

        # print(camera_y_limit_top, camera_y_limit_bottom)

        ### Handle x camera
        # First, we check if hero is closer to left_limit or right_limit
        # Then we act accordingly to that result
        # hero_x, hero_y = toPygame(hero_shape.body.position)
        if math.fabs(hero_x - camera_x_limit_left) < math.fabs(hero_x - camera_x_limit_right):
            # Here Hero is closer to left limit
            camera_pos_component.x = max(hero_x - WIN_WIDTH//2, camera_x_limit_left)

        # Get at least to the middle
        elif hero_x <= WIN_WIDTH//2:
            camera_pos_component.x = hero_x - WIN_WIDTH//2 + math.fabs(hero_x - WIN_WIDTH//2)

        else:
            # Here Hero is closer to right limit and at least in the middle of the screen
            if camera_x_limit_right >= WIN_WIDTH:
                # Radical solution, but it works for long distances. 
                if hero_x >= camera_x_limit_right - WIN_WIDTH//2 :
                    camera_pos_component.x = camera_x_limit_right - WIN_WIDTH
                else:
                    camera_pos_component.x = hero_x - WIN_WIDTH//2
            else:
                # For short distances, the following works better.
                camera_pos_component.x = min(hero_x - WIN_WIDTH//2, camera_x_limit_right - WIN_WIDTH//2)

        ## Handle y camera
        # Same process as x camera
        if math.fabs(hero_y - math.fabs(camera_y_limit_top)) < math.fabs(hero_y - math.fabs(camera_y_limit_bottom)):
            # Closer to top
            if camera_y_limit_top*-1 > WIN_HEIGHT:
                # print(1)
                a = hero_y - WIN_HEIGHT//2 #+ camera_y_limit_bottom
                b = math.fabs(camera_y_limit_top) - WIN_HEIGHT + camera_y_limit_bottom//2
            else:
                a = hero_y - WIN_HEIGHT//2 - camera_y_limit_bottom
                b = math.fabs(camera_y_limit_top) - WIN_HEIGHT - camera_y_limit_bottom
            # print(a, b, hero_y)            
            camera_pos_component.y = min(a, b)
        else:
            # Closer to bottom            
            camera_pos_component.y = max(hero_y - WIN_HEIGHT//2, math.fabs(camera_y_limit_bottom))










        # # x, y = helper.xyToPygame(100, camera_y_limit_top)
        # y = camera_y_limit_top
        # y += int(camera_pos_component.y)
        # y*= -1
        # x, y = helper.xyToPygame(100, y)
        # # print(y)
        # pygame.draw.circle(DISPLAYSURF, RED, (x, y), 50)